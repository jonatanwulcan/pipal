import threading
import time

import evdev
from evdev import InputDevice, ecodes

import plejd
import sonos

ALL_LEDS = [ecodes.LED_NUML, ecodes.LED_CAPSL, ecodes.LED_SCROLLL]

KEY_MAP = {
    ecodes.KEY_A: {"action": "sonos", "track": "https://open.spotify.com/track/24j01Gn8plo5U4gyYMPQws"},
    ecodes.KEY_B: {"action": "sonos", "track": "https://open.spotify.com/track/5ygDXis42ncn6kYG14lEVG"},
    ecodes.KEY_C: {"action": "sonos", "track": "https://open.spotify.com/track/5VpQpzSPO3adPtqKMGVYAD"},
    ecodes.KEY_D: {"action": "sonos", "track": "https://open.spotify.com/track/6FK3E5XGjp2ViJAG4i2OJ1"},
    ecodes.KEY_E: {"action": "sonos", "track": "https://open.spotify.com/track/7wPX68TYMcRFVuQXaWSZc2"},
    ecodes.KEY_F: {"action": "sonos", "track": "https://open.spotify.com/track/3v6FM4daF3FiOrLpvOTmO4"},
    ecodes.KEY_G: {"action": "sonos", "track": "https://open.spotify.com/track/5ZsbCNJeIZzeNGyplWY4M5"},
    ecodes.KEY_H: {"action": "sonos", "track": "https://open.spotify.com/track/1OK9kmDfGXendaE4QwzrAI"},
    ecodes.KEY_I: {"action": "sonos", "track": "https://open.spotify.com/track/3RriZsQmU4Jvp3Qh2oIZae"},
    ecodes.KEY_J: {"action": "sonos", "track": "https://open.spotify.com/track/2ndZlMYvcZu0GnZj2ZRAgj"},
    ecodes.KEY_K: {"action": "sonos", "track": "https://open.spotify.com/track/0gpzayawLbdlg37XvC43tU"},
    ecodes.KEY_L: {"action": "sonos", "track": "https://open.spotify.com/track/4wQhYF06be3fv1l3qUiODJ"},
    ecodes.KEY_M: {"action": "sonos", "track": "https://open.spotify.com/track/7CjLGz2MEU9vFssaZEXx8I"},
    ecodes.KEY_N: {"action": "sonos", "track": "https://open.spotify.com/track/00IsaSz12SMPxi6KzpAg3F"},
    ecodes.KEY_O: {"action": "sonos", "track": "https://open.spotify.com/track/0vwW2535lVhXVS4aXEjbHt"},
    ecodes.KEY_P: {"action": "sonos", "track": "https://open.spotify.com/track/46aGIv3vi8IZwseswGSdoB"},
    ecodes.KEY_Q: {"action": "sonos", "track": "https://open.spotify.com/track/2ELSVi4kwWOXgxiIC592tJ"},
    ecodes.KEY_R: {"action": "sonos", "track": "https://open.spotify.com/track/0gDgvbu5BD67XyWa9yU7Y5"},
    ecodes.KEY_S: {"action": "sonos", "track": "https://open.spotify.com/track/6Y6jq2el8dK1g00JppZXye"},
    ecodes.KEY_T: {"action": "sonos", "track": "https://open.spotify.com/track/3STU5Q4eapZJ5VbKsjsEOY"},
    ecodes.KEY_U: {"action": "sonos", "track": "https://open.spotify.com/track/72xYXlxyC33XhFmlwzrv61"},
    ecodes.KEY_V: {"action": "sonos", "track": "https://open.spotify.com/track/1CFWilgSeS4xbiZFYbQbUx"},
    ecodes.KEY_W: {"action": "sonos", "track": "https://open.spotify.com/track/63Tl9k1sH8tznn3bqoMuyF"},
    ecodes.KEY_X: {"action": "sonos", "track": "https://open.spotify.com/track/3Tp6XRivI85TAfpgja9ILh"},
    ecodes.KEY_Y: {"action": "sonos", "track": "https://open.spotify.com/track/1n15KtnkIknQUohNa9E0kT"},
    ecodes.KEY_Z: {"action": "sonos", "track": "https://open.spotify.com/track/49wOjOkS4pBK3PQnPnNYjb"},
    ecodes.KEY_LEFTBRACE:  {"action": "sonos", "track": "https://open.spotify.com/track/1bBgHQoZCJ5FzkxrkL1PQ9"},  # å
    ecodes.KEY_APOSTROPHE: {"action": "sonos", "track": "https://open.spotify.com/track/72ylSapVzIEe8QH4gssLwF"},  # ä
    ecodes.KEY_SEMICOLON:  {"action": "sonos", "track": "https://open.spotify.com/track/29fNIVCogo4jpvKgTtIwyb"},  # ö
    ecodes.KEY_F1:  {"action": "plejd", "dim": 21},
    ecodes.KEY_F2:  {"action": "plejd", "dim": 42},
    ecodes.KEY_F3:  {"action": "plejd", "dim": 63},
    ecodes.KEY_F4:  {"action": "plejd", "dim": 85},
    ecodes.KEY_F5:  {"action": "plejd", "dim": 106},
    ecodes.KEY_F6:  {"action": "plejd", "dim": 127},
    ecodes.KEY_F7:  {"action": "plejd", "dim": 148},
    ecodes.KEY_F8:  {"action": "plejd", "dim": 170},
    ecodes.KEY_F9:  {"action": "plejd", "dim": 191},
    ecodes.KEY_F10: {"action": "plejd", "dim": 212},
    ecodes.KEY_F11: {"action": "plejd", "dim": 233},
    ecodes.KEY_F12: {"action": "plejd", "dim": 255},
    ecodes.KEY_ESC: {"action": "plejd", "dim": None},
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
    plejd_module = plejd.PlejdModule(lambda busy: on_busy('plejd', busy))

    sonos_module.start()
    plejd_module.start()

    try:
        for event in keyboard.read_loop():
            if event.type != ecodes.EV_KEY or event.value != 1:
                continue

            binding = KEY_MAP.get(event.code)
            if not binding:
                continue

            if binding["action"] == "sonos":
                sonos_module.put(binding["track"])
            elif binding["action"] == "plejd":
                plejd_module.put(binding["dim"])

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
