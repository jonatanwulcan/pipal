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

KEY_MAP = {
    **{getattr(ecodes, f'KEY_{c.upper()}'): c for c in string.ascii_lowercase},
    ecodes.KEY_LEFTBRACE: 'å',
    ecodes.KEY_APOSTROPHE: 'ä',
    ecodes.KEY_SEMICOLON: 'ö',
}

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

    cancel_event = threading.Event()
    current_thread = None

    try:
        for event in keyboard.read_loop():
            if event.type != ecodes.EV_KEY or event.value != 1:
                continue

            code = drain_latest_key(keyboard, event.code)
            if code not in KEY_MAP:
                continue

            letter = KEY_MAP[code]
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
