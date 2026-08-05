import select
import string
import threading
import time

import evdev
from evdev import InputDevice, categorize, ecodes
import soco

SPEAKER_NAME = "Dags Room"
VOLUME = 30

ALL_LEDS = [ecodes.LED_NUML, ecodes.LED_CAPSL, ecodes.LED_SCROLLL]

LETTER_KEYS = {
    getattr(ecodes, f'KEY_{c.upper()}'): c
    for c in string.ascii_lowercase
}

# Map each letter to a Spotify track URI
TRACKS = {
    'a': 'spotify:track:PLACEHOLDER',
    'b': 'spotify:track:3ULkqRMNEabAFBPgh3vbm1',
    'c': 'spotify:track:PLACEHOLDER',
    'd': 'spotify:track:PLACEHOLDER',
    'e': 'spotify:track:PLACEHOLDER',
    'f': 'spotify:track:PLACEHOLDER',
    'g': 'spotify:track:PLACEHOLDER',
    'h': 'spotify:track:PLACEHOLDER',
    'i': 'spotify:track:PLACEHOLDER',
    'j': 'spotify:track:PLACEHOLDER',
    'k': 'spotify:track:PLACEHOLDER',
    'l': 'spotify:track:PLACEHOLDER',
    'm': 'spotify:track:PLACEHOLDER',
    'n': 'spotify:track:PLACEHOLDER',
    'o': 'spotify:track:PLACEHOLDER',
    'p': 'spotify:track:PLACEHOLDER',
    'q': 'spotify:track:PLACEHOLDER',
    'r': 'spotify:track:PLACEHOLDER',
    's': 'spotify:track:PLACEHOLDER',
    't': 'spotify:track:PLACEHOLDER',
    'u': 'spotify:track:PLACEHOLDER',
    'v': 'spotify:track:PLACEHOLDER',
    'w': 'spotify:track:PLACEHOLDER',
    'x': 'spotify:track:PLACEHOLDER',
    'y': 'spotify:track:PLACEHOLDER',
    'z': 'spotify:track:PLACEHOLDER',
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


def play_track(keyboard, track_uri, cancel):
    stop_anim = threading.Event()
    anim = threading.Thread(target=animate_leds, args=(keyboard, stop_anim), daemon=True)
    anim.start()

    try:
        speakers = soco.discover(timeout=2)
        if cancel.is_set():
            return

        speaker = next((s for s in (speakers or []) if s.player_name == SPEAKER_NAME), None)
        if not speaker:
            print(f"Speaker '{SPEAKER_NAME}' not found", flush=True)
            return
        if cancel.is_set():
            return

        coordinator = speaker.group.coordinator
        coordinator.volume = VOLUME
        if cancel.is_set():
            return

        coordinator.play_uri(track_uri)

        stop_anim.set()
        anim.join()
        set_leds(keyboard, 1)

        while not cancel.is_set():
            state = coordinator.get_current_transport_info()['current_transport_state']
            if state != 'PLAYING':
                break
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}", flush=True)
    finally:
        stop_anim.set()
        anim.join()
        set_leds(keyboard, 0)


def drain_latest_key(keyboard, initial_code):
    latest = initial_code
    while True:
        r, _, _ = select.select([keyboard.fd], [], [], 0)
        if not r:
            break
        for event in keyboard.read():
            if event.type == ecodes.EV_KEY and event.value == 1 and event.code in LETTER_KEYS:
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

    cancel_event = threading.Event()
    current_thread = None

    try:
        for event in keyboard.read_loop():
            if event.type != ecodes.EV_KEY or event.value != 1:
                continue

            code = drain_latest_key(keyboard, event.code)
            if code not in LETTER_KEYS:
                continue

            letter = LETTER_KEYS[code]
            track_uri = TRACKS.get(letter)
            if not track_uri:
                continue

            cancel_event.set()
            if current_thread and current_thread.is_alive():
                current_thread.join()

            cancel_event = threading.Event()
            current_thread = threading.Thread(
                target=play_track,
                args=(keyboard, track_uri, cancel_event),
                daemon=True,
            )
            current_thread.start()

    finally:
        cancel_event.set()
        if current_thread and current_thread.is_alive():
            current_thread.join()
        keyboard.ungrab()
        set_leds(keyboard, 0)


if __name__ == "__main__":
    main()
