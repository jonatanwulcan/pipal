import queue
import threading
import time

import soco
from soco.plugins.sharelink import ShareLinkPlugin

SPEAKER_NAME = "Dags Room"
VOLUME = 20

# Sentinel queued by stop_playback() to tell the worker to halt the speaker.
_STOP = object()


class SonosModule:
    def __init__(self, speaker_name: str = SPEAKER_NAME, volume: int = VOLUME):
        self._speaker_name = speaker_name
        self._volume = volume
        self._queue = queue.SimpleQueue()
        self._cancel = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.is_busy = False

    def start(self):
        self._thread.start()

    def put(self, urls):
        """Accepts a single share link URL or a list of URLs to play in order."""
        self._cancel.set()
        self._queue.put(urls)

    def stop_playback(self):
        """Halts whatever the speaker is currently playing."""
        self._cancel.set()
        self._queue.put(_STOP)

    def stop(self):
        self._cancel.set()
        self._queue.put(None)
        self._thread.join()

    def _run(self):
        while True:
            item = self._queue.get()
            if item is None:
                return

            # If more items are already queued, skip to the latest
            while not self._queue.empty():
                item = self._queue.get()
                if item is None:
                    return

            self._cancel.clear()
            self.is_busy = True
            try:
                if item is _STOP:
                    self._stop_playback()
                else:
                    self._play(item)
            except Exception as e:
                print(f"Sonos error: {e}", flush=True)
            finally:
                self.is_busy = False

    def _stop_playback(self):
        print("Sonos: discovering speakers", flush=True)
        speakers = soco.discover(timeout=2)
        speaker = next((s for s in (speakers or []) if s.player_name == self._speaker_name), None)
        if not speaker:
            print(f"Sonos: speaker '{self._speaker_name}' not found", flush=True)
            return
        print("Sonos: stopping playback", flush=True)
        speaker.stop()

    def _play(self, urls):
        if isinstance(urls, str):
            urls = [urls]
        print(f"Sonos: discovering speakers", flush=True)
        speakers = soco.discover(timeout=2)
        if self._cancel.is_set():
            return

        speaker = next((s for s in (speakers or []) if s.player_name == self._speaker_name), None)
        if not speaker:
            print(f"Sonos: speaker '{self._speaker_name}' not found", flush=True)
            return
        if self._cancel.is_set():
            return

        print(f"Sonos: playing {', '.join(urls)}", flush=True)
        speaker.unjoin()
        if self._cancel.is_set():
            return

        speaker.volume = self._volume
        if self._cancel.is_set():
            return

        share_link = ShareLinkPlugin(speaker)
        speaker.clear_queue()
        pos = None
        for url in urls:
            queued_at = share_link.add_share_link_to_queue(url)
            if pos is None:
                pos = queued_at
            if self._cancel.is_set():
                return

        # Stop at the end of the queue instead of repeating or shuffling
        speaker.play_mode = 'NORMAL'
        speaker.play_from_queue(pos - 1)
        print(f"Sonos: playback started", flush=True)

        while not self._cancel.is_set():
            state = speaker.get_current_transport_info()['current_transport_state']
            if state not in ('PLAYING', 'TRANSITIONING'):
                print(f"Sonos: playback ended ({state})", flush=True)
                break
            time.sleep(1)
