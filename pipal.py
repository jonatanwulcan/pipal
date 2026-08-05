import evdev
from evdev import InputDevice, categorize, ecodes

ALL_LEDS = [ecodes.LED_NUML, ecodes.LED_CAPSL, ecodes.LED_SCROLLL]

def find_keyboard():
    for path in evdev.list_devices():
        device = InputDevice(path)
        caps = device.capabilities()
        if ecodes.EV_KEY in caps:
            keys = caps[ecodes.EV_KEY]
            if ecodes.KEY_A in keys and ecodes.KEY_SPACE in keys:
                return device
    return None

def set_leds(device, state):
    for led in ALL_LEDS:
        device.set_led(led, state)

def main():
    keyboard = find_keyboard()
    if not keyboard:
        print("No keyboard found", flush=True)
        return

    print(f"Found keyboard: {keyboard.name}", flush=True)
    keyboard.grab()

    try:
        for event in keyboard.read_loop():
            if event.type == ecodes.EV_KEY:
                key = categorize(event)
                if key.keystate == key.key_down:
                    set_leds(keyboard, 1)
                elif key.keystate == key.key_up:
                    set_leds(keyboard, 0)
    finally:
        keyboard.ungrab()
        set_leds(keyboard, 0)

if __name__ == "__main__":
    main()
