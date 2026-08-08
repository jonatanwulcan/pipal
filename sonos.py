import queue
import threading
import time

import soco
from soco.plugins.sharelink import ShareLinkPlugin

SPEAKER_NAME = "Dags Room"
VOLUME = 20


class SonosModule:
    def __init__(self, on_busy, speaker_name: str = SPEAKER_NAME, volume: int = VOLUME):
        self._speaker_name = speaker_name
        self._volume = volume
        self._on_busy = on_busy
        self._queue = queue.SimpleQueue()
        self._cancel = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def put(self, url: str):
        self._cancel.set()
        self._queue.put(url)

    def stop(self):
        self._cancel.set()
        self._queue.put(None)
        self._thread.join()

    def _run(self):
        while True:
            url = self._queue.get()
            if url is None:
                return

            # If more items are already queued, skip to the latest
            while not self._queue.empty():
                url = self._queue.get()
                if url is None:
                    return

            self._cancel.clear()
            self._on_busy(True)
            try:
                self._play(url)
            except Exception as e:
                print(f"Sonos error: {e}", flush=True)
            finally:
                self._on_busy(False)

    def _play(self, url: str):
        speakers = soco.discover(timeout=2)
        if self._cancel.is_set():
            return

        speaker = next((s for s in (speakers or []) if s.player_name == self._speaker_name), None)
        if not speaker:
            print(f"Sonos: speaker '{self._speaker_name}' not found", flush=True)
            return
        if self._cancel.is_set():
            return

        speaker.unjoin()
        if self._cancel.is_set():
            return

        speaker.volume = self._volume
        if self._cancel.is_set():
            return

        share_link = ShareLinkPlugin(speaker)
        speaker.clear_queue()
        pos = share_link.add_share_link_to_queue(url)
        speaker.play_from_queue(pos - 1)

        while not self._cancel.is_set():
            state = speaker.get_current_transport_info()['current_transport_state']
            if state not in ('PLAYING', 'TRANSITIONING'):
                break
            time.sleep(1)
