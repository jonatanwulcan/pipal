import asyncio
import hashlib
import json
import os
import threading
import traceback

import aiohttp
from bleak import BleakClient, BleakScanner
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_SUFFIX  = "6085-4726-be45-040c957391b5"
SERVICE  = f"31ba0001-{_SUFFIX}"
_AUTH    = f"31ba0009-{_SUFFIX}"
_PING    = f"31ba000a-{_SUFFIX}"
_DATA    = f"31ba0004-{_SUFFIX}"

_API_BASE = "https://cloud.plejd.com"
_API_HEADERS = {
    "X-Parse-Application-Id": "zHtVqXt8k4yFyk2QGmgp48D9xZr2G94xWYnF4dak",
    "Content-Type": "application/json",
}

_CMD_STATE       = 0x0097
_CMD_STATE_LEVEL = 0x0098


async def _restart_bluetooth():
    print("Plejd: restarting bluetooth service", flush=True)
    proc = await asyncio.create_subprocess_exec(
        "sudo", "systemctl", "restart", "bluetooth",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()
    print("Plejd: bluetooth service restarted", flush=True)


def _encrypt_decrypt(key_hex: str, addr_hex: str, data: bytes) -> bytes:
    key  = bytes.fromhex(key_hex.replace("-", ""))
    addr = bytes.fromhex(addr_hex.replace(":", "").replace("-", ""))[::-1]
    buf  = addr + addr + addr[:4]
    ct   = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend()).encryptor().update(buf)
    return bytes(d ^ ct[i % 16] for i, d in enumerate(data))


def _auth_response(key_hex: str, challenge: bytes) -> bytes:
    key          = bytes.fromhex(key_hex.replace("-", ""))
    intermediate = hashlib.sha256(((int.from_bytes(key, "big") ^ int.from_bytes(challenge, "big")).to_bytes(16, "big"))).digest()
    return bytes(a ^ b for a, b in zip(intermediate[:16], intermediate[16:]))


def _build_command(address: int, dim: int | None) -> bytes:
    if dim is None:
        return bytes([address, 0x01, 0x10, *_CMD_STATE.to_bytes(2), 0x00])
    return bytes([address, 0x01, 0x10, *_CMD_STATE_LEVEL.to_bytes(2), 0x01, dim, dim])


async def _fetch_cryptokey(username: str, password: str, site_id: str) -> str:
    async with aiohttp.ClientSession(_API_BASE, headers=_API_HEADERS) as session:
        resp = await session.post("/parse/login", json={"username": username, "password": password})
        resp.raise_for_status()
        token = (await resp.json())["sessionToken"]
        session.headers["X-Parse-Session-Token"] = token
        resp = await session.post("/parse/functions/getSiteById", params={"siteId": site_id})
        resp.raise_for_status()
        return (await resp.json())["result"][0]["plejdMesh"]["cryptoKey"]


class PlejdConnection:
    def __init__(self, username: str, password: str, site_id: str):
        self._username  = username
        self._password  = password
        self._site_id   = site_id
        self._cryptokey = None
        self._client    = None
        self._gw_mac    = None
        self._lock      = None

    async def _get_lock(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def _on_disconnect(self, _client):
        print("Plejd: disconnected from mesh", flush=True)
        self._client = None
        self._gw_mac = None

    async def _connect(self):
        bluetooth_restarted = False
        while True:
            try:
                if not self._cryptokey:
                    print("Plejd: fetching cryptokey from cloud", flush=True)
                    self._cryptokey = await _fetch_cryptokey(self._username, self._password, self._site_id)

                print("Plejd: scanning for mesh nodes", flush=True)
                devices = await BleakScanner.discover(timeout=2.0, service_uuids=[SERVICE], return_adv=True)
                if not devices:
                    if not bluetooth_restarted:
                        await _restart_bluetooth()
                        bluetooth_restarted = True
                    raise RuntimeError("no mesh nodes found during BLE scan")

                for dev, adv in devices.values():
                    print(f"Plejd: found node {dev.address} (RSSI {adv.rssi})", flush=True)

                best_device, best_adv = max(devices.values(), key=lambda x: x[1].rssi)
                print(f"Plejd: connecting to {best_device.address} (RSSI {best_adv.rssi})", flush=True)

                client = BleakClient(best_device, disconnected_callback=self._on_disconnect)
                await client.connect()

                print("Plejd: authenticating", flush=True)
                await client.write_gatt_char(_AUTH, b"\x00", response=True)
                challenge = bytes(await client.read_gatt_char(_AUTH))
                await client.write_gatt_char(_AUTH, _auth_response(self._cryptokey, challenge), response=True)

                ping = bytes([os.urandom(1)[0]])
                await client.write_gatt_char(_PING, ping, response=True)
                pong = bytes(await client.read_gatt_char(_PING))
                if (ping[0] + 1) & 0xFF != pong[0]:
                    await client.disconnect()
                    raise RuntimeError("authentication failed (bad ping/pong)")

                self._gw_mac = best_device.address
                self._client = client
                print("Plejd: connected to mesh", flush=True)
                return
            except RuntimeError as e:
                print(f"Plejd: connect failed ({e}), retrying in 5s", flush=True)
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Plejd: connect failed ({e}), retrying in 5s\n{traceback.format_exc()}", flush=True)
                await asyncio.sleep(5)

    async def warmup(self):
        lock = await self._get_lock()
        async with lock:
            await self._connect()

    async def send(self, address: int, dim: int | None):
        lock = await self._get_lock()
        async with lock:
            if self._client is None or self._gw_mac is None:
                raise RuntimeError("not connected")
            action = f"dim={dim}" if dim is not None else "off"
            print(f"Plejd: sending {action} to address {address}", flush=True)
            cmd = _build_command(address, dim)
            encrypted = _encrypt_decrypt(self._cryptokey, self._gw_mac, cmd)
            await self._client.write_gatt_char(_DATA, encrypted, response=True)

    async def _health_check_loop(self):
        while True:
            await asyncio.sleep(60)
            lock = await self._get_lock()
            async with lock:
                if self._client is None or self._gw_mac is None:
                    print("Plejd: health check: not connected, reconnecting", flush=True)
                    await self._connect()
                    continue
                try:
                    ping = bytes([os.urandom(1)[0]])
                    await self._client.write_gatt_char(_PING, ping, response=True)
                    pong = bytes(await self._client.read_gatt_char(_PING))
                    if (ping[0] + 1) & 0xFF != pong[0]:
                        raise RuntimeError("bad ping/pong")
                except RuntimeError as e:
                    print(f"Plejd: health check failed ({e}), reconnecting", flush=True)
                    self._client = None
                    self._gw_mac = None
                    await self._connect()
                except Exception as e:
                    print(f"Plejd: health check failed ({e}), reconnecting\n{traceback.format_exc()}", flush=True)
                    self._client = None
                    self._gw_mac = None
                    await self._connect()

    async def close(self):
        if self._client:
            await self._client.disconnect()
            self._client = None


CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plejd_credentials.json")
PLEJD_ADDRESS = 18  # Skrivbord


class PlejdModule:
    def __init__(self, credentials_file: str = CREDENTIALS_FILE, address: int = PLEJD_ADDRESS):
        with open(credentials_file) as f:
            creds = json.load(f)
        self._address  = address
        self._conn     = PlejdConnection(creds["username"], creds["password"], creds["siteId"])
        self._loop     = asyncio.new_event_loop()
        self._thread   = threading.Thread(target=self._loop.run_forever, daemon=True)
        self.is_busy   = False

    def start(self):
        self._thread.start()
        asyncio.run_coroutine_threadsafe(self._conn.warmup(), self._loop)
        asyncio.run_coroutine_threadsafe(self._conn._health_check_loop(), self._loop)

    def put(self, dim: int | None):
        asyncio.run_coroutine_threadsafe(self._send(dim), self._loop)

    def stop(self):
        asyncio.run_coroutine_threadsafe(self._conn.close(), self._loop).result(timeout=5)
        self._loop.call_soon_threadsafe(self._loop.stop)

    async def _send(self, dim: int | None):
        self.is_busy = True
        action = f"dim={dim}" if dim is not None else "off"
        try:
            await self._conn.send(self._address, dim)
        except RuntimeError as e:
            print(f"Plejd: dropped command ({action}): {e}", flush=True)
        except Exception as e:
            print(f"Plejd: error sending command ({action}): {e}\n{traceback.format_exc()}", flush=True)
        finally:
            self.is_busy = False
