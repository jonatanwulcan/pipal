import json
import os
import select
import string
import threading
import time

import evdev
from evdev import InputDevice, ecodes

import plejd
import sonos

PLEJD_ADDRESS = 18  # Skrivbord
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plejd_credentials.json")

ALL_LEDS = [ecodes.LED_NUML, ecodes.LED_CAPSL, ecodes.LED_SCROLLL]

KEY_MAP = {
    **{getattr(ecodes, f'KEY_{c.upper()}'): c for c in string.ascii_lowercase},
    ecodes.KEY_LEFTBRACE: 'å',
    ecodes.KEY_APOSTROPHE: 'ä',
    ecodes.KEY_SEMICOLON: 'ö',
}

_f_keys = [
    ecodes.KEY_F1, ecodes.KEY_F2, ecodes.KEY_F3, ecodes.KEY_F4,
    ecodes.KEY_F5, ecodes.KEY_F6, ecodes.KEY_F7, ecodes.KEY_F8,
    ecodes.KEY_F9, ecodes.KEY_F10, ecodes.KEY_F11, ecodes.KEY_F12,
]
PLEJD_KEY_MAP = {key: int(255 * (i + 1) / 12) for i, key in enumerate(_f_keys)}
PLEJD_KEY_MAP[ecodes.KEY_ESC] = None

TRACKS = {
    'a': 'https://open.spotify.com/track/24j01Gn8plo5U4gyYMPQws',
    'b': 'https://open.spotify.com/track/5ygDXis42ncn6kYG14lEVG',
    'c': 'https://open.spotify.com/track/5VpQpzSPO3adPtqKMGVYAD',
    'd': 'https://open.spotify.com/track/6FK3E5XGjp2ViJAG4i2OJ1',
    'e': 'https://open.spotify.com/track/7wPX68TYMcRFVuQXaWSZc2',
    'f': 'https://open.spotify.com/track/3v6FM4daF3FiOrLpvOTmO4',
    'g': 'https://open.spotify.com/track/5ZsbCNJeIZzeNGyplWY4M5',
    'h': 'https://open.spotify.com/track/1OK9kmDfGXendaE4QwzrAI',
    'i': 'https://open.spotify.com/track/3RriZsQmU4Jvp3Qh2oIZae',
    'j': 'https://open.spotify.com/track/2ndZlMYvcZu0GnZj2ZRAgj',
    'k': 'https://open.spotify.com/track/0gpzayawLbdlg37XvC43tU',
    'l': 'https://open.spotify.com/track/4wQhYF06be3fv1l3qUiODJ',
    'm': 'https://open.spotify.com/track/7CjLGz2MEU9vFssaZEXx8I',
    'n': 'https://open.spotify.com/track/00IsaSz12SMPxi6KzpAg3F',
    'o': 'https://open.spotify.com/track/0vwW2535lVhXVS4aXEjbHt',
    'p': 'https://open.spotify.com/track/46aGIv3vi8IZwseswGSdoB',
    'q': 'https://open.spotify.com/track/2ELSVi4kwWOXgxiIC592tJ',
    'r': 'https://open.spotify.com/track/0gDgvbu5BD67XyWa9yU7Y5',
    's': 'https://open.spotify.com/track/6Y6jq2el8dK1g00JppZXye',
    't': 'https://open.spotify.com/track/3STU5Q4eapZJ5VbKsjsEOY',
    'u': 'https://open.spotify.com/track/72xYXlxyC33XhFmlwzrv61',
    'v': 'https://open.spotify.com/track/1CFWilgSeS4xbiZFYbQbUx',
    'w': 'https://open.spotify.com/track/63Tl9k1sH8tznn3bqoMuyF',
    'x': 'https://open.spotify.com/track/3Tp6XRivI85TAfpgja9ILh',
    'y': 'https://open.spotify.com/track/1n15KtnkIknQUohNa9E0kT',
    'z': 'https://open.spotify.com/track/49wOjOkS4pBK3PQnPnNYjb',
    'å': 'https://open.spotify.com/track/1bBgHQoZCJ5FzkxrkL1PQ9',
    'ä': 'https://open.spotify.com/track/72ylSapVzIEe8QH4gssLwF',
    'ö': 'https://open.spotify.com/track/29fNIVCogo4jpvKgTtIwyb',
}


def set_leds(keyboard, state):
    for led in ALL_LEDS:
        keyboard.set_led(led, state)


def animate_leds(keyboard, stop_event):
    idx = 0
    while not stop_event.is_set():
        for led in ALL_LEDS:
            keyboard.set_led(led, 0)
        keyboard.set_led(ALL_LEDS[idx % 3], 1)
        idx += 1
        time.sleep(0.2)


def drain_latest_key(keyboard, initial_code):
    latest = initial_code
    while True:
        r, _, _ = select.select([keyboard.fd], [], [], 0)
        if not r:
            break
        for event in keyboard.read():
            if event.type == ecodes.EV_KEY and event.value == 1 and event.code in KEY_MAP:
                latest = event.code
    return latest


def find_keyboard():
    for path in evdev.list_devices():
        device = InputDevice(path)
        caps = device.capabilities()
        if ecodes.EV_KEY in caps:
            keys = caps[ecodes.EV_KEY]
            if ecodes.KEY_A in keys and ecodes.KEY_SPACE in keys:
                return device
    return None


def main():
    keyboard = find_keyboard()
    if not keyboard:
        print("No keyboard found", flush=True)
        return

    print(f"Found keyboard: {keyboard.name}", flush=True)
    keyboard.grab()

    with open(CREDENTIALS_FILE) as f:
        creds = json.load(f)

    busy_modules = set()
    busy_lock = threading.Lock()
    blink_stop = threading.Event()
    blink_thread = None

    def on_busy(name, is_busy):
        nonlocal blink_thread
        with busy_lock:
            if is_busy:
                busy_modules.add(name)
            else:
                busy_modules.discard(name)
            if busy_modules:
                if blink_thread is None or not blink_thread.is_alive():
                    blink_stop.clear()
                    blink_thread = threading.Thread(target=animate_leds, args=(keyboard, blink_stop), daemon=True)
                    blink_thread.start()
            else:
                blink_stop.set()
                set_leds(keyboard, 0)

    sonos_module = sonos.SonosModule(lambda busy: on_busy('sonos', busy))
    plejd_module = plejd.PlejdModule(creds["username"], creds["password"], creds["siteId"], PLEJD_ADDRESS, lambda busy: on_busy('plejd', busy))

    sonos_module.start()
    plejd_module.start()

    try:
        for event in keyboard.read_loop():
            if event.type != ecodes.EV_KEY or event.value != 1:
                continue

            code = event.code

            if code in PLEJD_KEY_MAP:
                plejd_module.put(PLEJD_KEY_MAP[code])

            elif code in KEY_MAP:
                code = drain_latest_key(keyboard, code)
                url = TRACKS.get(KEY_MAP[code])
                if url:
                    sonos_module.put(url)

    finally:
        sonos_module.stop()
        plejd_module.stop()
        blink_stop.set()
        if blink_thread and blink_thread.is_alive():
            blink_thread.join()
        keyboard.ungrab()
        set_leds(keyboard, 0)


if __name__ == "__main__":
    main()
