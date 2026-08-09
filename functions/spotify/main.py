import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
from google.cloud import secretmanager
import firebase_admin
from firebase_admin import auth as firebase_auth
import requests as http

app = Flask(__name__)
firebase_admin.initialize_app()

ALLOWED_EMAILS = {'jonatan.wulcan@gmail.com', 'karin.wulcan@gmail.com'}

_credentials = None
_token = None
_token_expiry = 0


def verify_firebase_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    id_token = auth_header[7:]
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded.get('email') in ALLOWED_EMAILS
    except Exception as e:
        app.logger.warning('Token verification failed: %s', e)
        return False


def get_credentials():
    global _credentials
    if _credentials:
        return _credentials
    client = secretmanager.SecretManagerServiceClient()
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "pipal-app")

    def fetch(name):
        resource = f"projects/{project}/secrets/{name}/versions/latest"
        return client.access_secret_version(name=resource).payload.data.decode().strip()

    _credentials = (fetch("spotify-client-id"), fetch("spotify-client-secret"))
    return _credentials


def get_token():
    global _token, _token_expiry
    if _token and time.time() < _token_expiry:
        return _token
    client_id, client_secret = get_credentials()
    resp = http.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    resp.raise_for_status()
    result = resp.json()
    _token = result["access_token"]
    _token_expiry = time.time() + result["expires_in"] - 60
    return _token


def fetch_one(token, track_id):
    resp = http.get(
        f"https://api.spotify.com/v1/tracks/{track_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if not resp.ok:
        app.logger.error("Spotify track %s error %s: %s", track_id, resp.status_code, resp.text)
        return None
    track = resp.json()
    return (track["id"], {"name": track["name"]})


@app.route("/api/tracks")
def tracks():
    if not verify_firebase_token():
        return jsonify({}), 401

    ids = [i.strip() for i in request.args.get("ids", "").split(",") if i.strip()]
    if not ids:
        return jsonify({})

    token = get_token()
    result = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_one, token, tid): tid for tid in ids[:50]}
        for future in as_completed(futures):
            entry = future.result()
            if entry:
                result[entry[0]] = entry[1]
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
