import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
from google.cloud import secretmanager
import requests as http

app = Flask(__name__)

_credentials = None
_token = None
_token_expiry = 0


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


@app.route("/api/debug")
def debug():
    token = get_token()
    no_auth = http.get("https://api.spotify.com/v1/markets")
    with_auth = http.get("https://api.spotify.com/v1/markets", headers={"Authorization": f"Bearer {token}"})
    return jsonify({
        "token_prefix": token[:10],
        "no_auth_status": no_auth.status_code,
        "with_auth_status": with_auth.status_code,
        "with_auth_body": with_auth.text[:300],
    })


def fetch_one(token, track_id):
    resp = http.get(
        f"https://api.spotify.com/v1/tracks/{track_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if not resp.ok:
        app.logger.error("Spotify track %s error %s: %s", track_id, resp.status_code, resp.text)
        return None
    track = resp.json()
    return (track["id"], {
        "name": track["name"],
        "artists": ", ".join(a["name"] for a in track["artists"]),
    })


@app.route("/api/tracks")
def tracks():
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
