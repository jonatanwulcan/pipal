#!/usr/bin/env python3
"""Quick test: look up a Spotify track by ID using credentials from GCP Secret Manager."""

import sys
import base64
import urllib.request
import urllib.parse
import json
from google.cloud import secretmanager


def get_secret(project_id, name):
    client = secretmanager.SecretManagerServiceClient()
    resource = f"projects/{project_id}/secrets/{name}/versions/latest"
    return client.access_secret_version(name=resource).payload.data.decode().strip()


def get_token(client_id, client_secret):
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def lookup_track(token, track_id):
    req = urllib.request.Request(
        f"https://api.spotify.com/v1/tracks/{track_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    track_id = sys.argv[1] if len(sys.argv) > 1 else "4uLU6hMCjMI75M1A2tKUQC"
    project_id = "pipal-app"

    client_id = get_secret(project_id, "spotify-client-id")
    client_secret = get_secret(project_id, "spotify-client-secret")
    token = get_token(client_id, client_secret)
    track = lookup_track(token, track_id)

    artists = ", ".join(a["name"] for a in track["artists"])
    print(f"{track['name']} — {artists}")
