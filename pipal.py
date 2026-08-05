import select
import string
import threading
import time

import evdev
from evdev import InputDevice, categorize, ecodes
import soco
from soco.plugins.sharelink import ShareLinkPlugin

SPEAKER_NAME = "Dags Room"
VOLUME = 20

ALL_LEDS = [ecodes.LED_NUML, ecodes.LED_CAPSL, ecodes.LED_SCROLLL]

LETTER_KEYS = {
    getattr(ecodes, f'KEY_{c.upper()}'): c
    for c in string.ascii_lowercase
}

# Map each letter to a Spotify track URL
TRACKS = {
    'b': 'https://open.spotify.com/track/3ULkqRMNEabAFBPgh3vbm1',  # Baby Shark
    'd': 'https://open.spotify.com/track/39H5u7s9WJ0vDF8nR7BL31',  # We Are The Dinos
    'g': 'https://open.spotify.com/track/3K6RAO0MAx5n3Agffwa69L',  # Små grodorna
    'k': 'https://open.spotify.com/track/7kq6PnA3PYvzfCZN6P7Aqg',  # Krokodilen i bilen
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


def play_track(keyboard, track_url, cancel):
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

        speaker.unjoin()
        if cancel.is_set():
            return

        speaker.volume = VOLUME
        if cancel.is_set():
            return

        share_link = ShareLinkPlugin(speaker)
        speaker.clear_queue()
        queue_position = share_link.add_share_link_to_queue(track_url)
        speaker.play_from_queue(queue_position - 1)

        stop_anim.set()
        anim.join()
        set_leds(keyboard, 1)

        while not cancel.is_set():
            state = speaker.get_current_transport_info()['current_transport_state']
            if state not in ('PLAYING', 'TRANSITIONING'):
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
            track_url = TRACKS.get(letter)
            if not track_url:
                continue

            cancel_event.set()
            if current_thread and current_thread.is_alive():
                current_thread.join()

            cancel_event = threading.Event()
            current_thread = threading.Thread(
                target=play_track,
                args=(keyboard, track_url, cancel_event),
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
