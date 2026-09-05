import json
import os
import queue
import smtplib
import threading
from email.message import EmailMessage

SMTP_HOST = "smtp.mail.me.com"
SMTP_PORT = 587

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facetime_credentials.json")


class FacetimeModule:
    """Sends a trigger email to the iPad's own iCloud account. Each key has a
    high-entropy random subject line; a Shortcuts automation on the iPad
    matches on that subject to start a FaceTime call to the right person."""

    def __init__(self, credentials_file: str = CREDENTIALS_FILE):
        with open(credentials_file) as f:
            creds = json.load(f)
        self._username = creds["username"]
        self._password = creds["password"]
        self._keys = creds["keys"]
        self._queue = queue.SimpleQueue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.is_busy = False

    def start(self):
        self._thread.start()

    def put(self, key_name: str):
        self._queue.put(key_name)

    def stop(self):
        self._queue.put(None)
        self._thread.join()

    def _run(self):
        while True:
            key_name = self._queue.get()
            if key_name is None:
                return

            self.is_busy = True
            try:
                self._send(key_name)
            except Exception as e:
                print(f"Facetime error: {e}", flush=True)
            finally:
                self.is_busy = False

    def _send(self, key_name: str):
        subject = self._keys.get(key_name)
        if not subject:
            print(f"Facetime: no trigger configured for key '{key_name}'", flush=True)
            return

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self._username
        msg["To"] = self._username
        msg.set_content("pipal trigger")

        print(f"Facetime: sending trigger for '{key_name}'", flush=True)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(self._username, self._password)
            smtp.send_message(msg)
        print(f"Facetime: trigger sent for '{key_name}'", flush=True)
