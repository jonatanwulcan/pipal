import hashlib
import os

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

# Command codes
_CMD_STATE       = 0x0097  # on/off only
_CMD_STATE_LEVEL = 0x0098  # on + dim level


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


async def control(username: str, password: str, site_id: str, address: int, dim: int | None) -> None:
    cryptokey = await _fetch_cryptokey(username, password, site_id)

    devices = await BleakScanner.discover(timeout=2.0, service_uuids=[SERVICE], return_adv=True)
    if not devices:
        raise RuntimeError("No Plejd mesh devices found")

    best_device, _ = max(devices.values(), key=lambda x: x[1].rssi)

    async with BleakClient(best_device) as client:
        await client.write_gatt_char(_AUTH, b"\x00", response=True)
        challenge = bytes(await client.read_gatt_char(_AUTH))
        await client.write_gatt_char(_AUTH, _auth_response(cryptokey, challenge), response=True)

        ping = bytes([os.urandom(1)[0]])
        await client.write_gatt_char(_PING, ping, response=True)
        pong = bytes(await client.read_gatt_char(_PING))
        if (ping[0] + 1) & 0xFF != pong[0]:
            raise RuntimeError("Plejd authentication failed")

        cmd = _build_command(address, dim)
        await client.write_gatt_char(_DATA, _encrypt_decrypt(cryptokey, best_device.address, cmd), response=True)
