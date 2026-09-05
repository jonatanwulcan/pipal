import random
import threading
import time

import evdev
from evdev import InputDevice, ecodes
from google.auth.credentials import AnonymousCredentials
from google.cloud import firestore

import facetime
import plejd
import sonos
import stories

ALL_LEDS = [ecodes.LED_NUML, ecodes.LED_CAPSL, ecodes.LED_SCROLLL]

# Letter keys on the keyboard map to different evdev codes depending on layout.
# The Pi uses a Swedish layout where Å/Ä/Ö land on these physical keys.
LETTER_TO_EVDEV = {
    'A': ecodes.KEY_A, 'B': ecodes.KEY_B, 'C': ecodes.KEY_C,
    'D': ecodes.KEY_D, 'E': ecodes.KEY_E, 'F': ecodes.KEY_F,
    'G': ecodes.KEY_G, 'H': ecodes.KEY_H, 'I': ecodes.KEY_I,
    'J': ecodes.KEY_J, 'K': ecodes.KEY_K, 'L': ecodes.KEY_L,
    'M': ecodes.KEY_M, 'N': ecodes.KEY_N, 'O': ecodes.KEY_O,
    'P': ecodes.KEY_P, 'Q': ecodes.KEY_Q, 'R': ecodes.KEY_R,
    'S': ecodes.KEY_S, 'T': ecodes.KEY_T, 'U': ecodes.KEY_U,
    'V': ecodes.KEY_V, 'W': ecodes.KEY_W, 'X': ecodes.KEY_X,
    'Y': ecodes.KEY_Y, 'Z': ecodes.KEY_Z,
    'Å': ecodes.KEY_LEFTBRACE,
    'Ä': ecodes.KEY_APOSTROPHE,
    'Ö': ecodes.KEY_SEMICOLON,
}

# F1 is the lowest dim level (0, which is not off for Plejd) and F12 is full.
# The gamma curve makes the perceived brightness steps feel linear.
DIM_GAMMA = 1.5
F_KEYS = [
    ecodes.KEY_F1, ecodes.KEY_F2, ecodes.KEY_F3, ecodes.KEY_F4,
    ecodes.KEY_F5, ecodes.KEY_F6, ecodes.KEY_F7, ecodes.KEY_F8,
    ecodes.KEY_F9, ecodes.KEY_F10, ecodes.KEY_F11, ecodes.KEY_F12,
]

PLEJD_ENTRIES = {
    key: {"action": "plejd", "dim": round(255 * (i / (len(F_KEYS) - 1)) ** DIM_GAMMA)}
    for i, key in enumerate(F_KEYS)
}
PLEJD_ENTRIES[ecodes.KEY_ESC] = {"action": "plejd", "dim": None}

# The 6-key cluster above the arrow keys, one per family member, each calling
# out to a distinct Shortcuts automation on the iPad via facetime.py.
FACETIME_ENTRIES = {
    ecodes.KEY_INSERT: {"action": "facetime", "key": "INSERT"},
    ecodes.KEY_HOME: {"action": "facetime", "key": "HOME"},
    ecodes.KEY_PAGEUP: {"action": "facetime", "key": "PAGEUP"},
    ecodes.KEY_DELETE: {"action": "facetime", "key": "DELETE"},
    ecodes.KEY_END: {"action": "facetime", "key": "END"},
    ecodes.KEY_PAGEDOWN: {"action": "facetime", "key": "PAGEDOWN"},
}

# Static bindings that are always present regardless of Firestore config.
STATIC_ENTRIES = dict(PLEJD_ENTRIES)
STATIC_ENTRIES[ecodes.KEY_SPACE] = {"action": "story"}
STATIC_ENTRIES.update(FACETIME_ENTRIES)

KEY_MAP = dict(STATIC_ENTRIES)


def _build_sonos_entries(keybindings):
    entries = {}
    for letter, evdev_code in LETTER_TO_EVDEV.items():
        v = keybindings.get(letter)
        if v and v.get('trackId'):
            url = f"https://open.spotify.com/track/{v['trackId']}"
        elif v and v.get('albumId'):
            url = f"https://open.spotify.com/album/{v['albumId']}"
        else:
            continue
        entries[evdev_code] = {"action": "sonos", "track": url}
    return entries


def _on_config_snapshot(doc_snapshots, changes, read_time):
    global KEY_MAP
    print("Firestore: received config snapshot", flush=True)
    for snap in doc_snapshots:
        if not snap.exists:
            print("Firestore: configuration document missing in snapshot", flush=True)
            continue
        try:
            keybindings = snap.get('keybindings') or {}
            sonos_entries = _build_sonos_entries(keybindings)
            old_map = KEY_MAP
            new_map = dict(STATIC_ENTRIES)
            new_map.update(sonos_entries)
            KEY_MAP = new_map

            changed = [
                f"  {letter}: {sonos_entries.get(code, {}).get('track', '(removed)')}"
                for letter, code in LETTER_TO_EVDEV.items()
                if old_map.get(code, {}).get('track') != sonos_entries.get(code, {}).get('track')
            ]
            if changed:
                print(f"Firestore: {len(changed)} key(s) updated:", flush=True)
                for line in changed:
                    print(line, flush=True)
            else:
                print("Firestore: snapshot received, no changes", flush=True)
        except Exception as e:
            print(f"Firestore: error processing snapshot: {e}", flush=True)


def load_keybindings():
    """Blocking initial fetch from Firestore, then starts a live listener."""
    print("Firestore: connecting...", flush=True)
    db = firestore.Client(project='pipal-app', credentials=AnonymousCredentials())
    config_ref = db.collection('configuration').document('main')

    snap = config_ref.get()
    if not snap.exists:
        raise RuntimeError("Firestore: configuration document not found")

    keybindings = snap.get('keybindings') or {}
    sonos_entries = _build_sonos_entries(keybindings)
    global KEY_MAP
    KEY_MAP = dict(STATIC_ENTRIES)
    KEY_MAP.update(sonos_entries)

    print(f"Firestore: loaded {len(sonos_entries)} song keys:", flush=True)
    for letter, code in LETTER_TO_EVDEV.items():
        entry = sonos_entries.get(code)
        track = entry['track'] if entry else '(missing)'
        print(f"  {letter}: {track}", flush=True)

    config_ref.on_snapshot(_on_config_snapshot)
    print("Firestore: live listener started", flush=True)
    return db  # keep reference alive so the listener isn't GC'd


def set_leds(keyboard, state):
    for led in ALL_LEDS:
        keyboard.set_led(led, state)


def manage_leds(keyboard, modules, stop_event):
    idx = 0
    while not stop_event.is_set():
        if any(m.is_busy for m in modules):
            for led in ALL_LEDS:
                keyboard.set_led(led, 0)
            keyboard.set_led(ALL_LEDS[idx % 3], 1)
            idx += 1
        else:
            set_leds(keyboard, 0)
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
    db = load_keybindings()

    keyboard = find_keyboard()
    if not keyboard:
        print("No keyboard found", flush=True)
        return

    print(f"Found keyboard: {keyboard.name}", flush=True)
    keyboard.grab()

    sonos_module = sonos.SonosModule()
    plejd_module = plejd.PlejdModule()
    facetime_module = facetime.FacetimeModule()

    sonos_module.start()
    plejd_module.start()
    facetime_module.start()

    led_stop = threading.Event()
    led_thread = threading.Thread(target=manage_leds, args=(keyboard, [sonos_module, plejd_module, facetime_module], led_stop), daemon=True)
    led_thread.start()

    try:
        for event in keyboard.read_loop():
            if event.type != ecodes.EV_KEY or event.value != 1:
                continue

            binding = KEY_MAP.get(event.code)
            if not binding:
                continue

            if binding["action"] == "sonos":
                sonos_module.put(binding["track"])
            elif binding["action"] == "story":
                story = random.choice(stories.STORIES)
                print(f"Story: {story['title']}", flush=True)
                sonos_module.put([
                    f"https://open.spotify.com/track/{track_id}"
                    for track_id in story["tracks"]
                ])
            elif binding["action"] == "plejd":
                plejd_module.put(binding["dim"])
            elif binding["action"] == "facetime":
                facetime_module.put(binding["key"])

    finally:
        led_stop.set()
        led_thread.join(timeout=0.5)
        sonos_module.stop()
        plejd_module.stop()
        facetime_module.stop()
        keyboard.ungrab()
        set_leds(keyboard, 0)


if __name__ == "__main__":
    main()
