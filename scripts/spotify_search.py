#!/usr/bin/env python3
"""Search Spotify using credentials fetched on the fly from GCP Secret Manager.

Credentials and tokens are kept in memory only and never printed.

Usage:
  spotify_search.py search "query" [--type album|track] [--limit N]
  spotify_search.py album <album_id>            # list tracks with durations
  spotify_search.py albums-by-artist <artist_id> [--limit N]
"""
import argparse
import json
import subprocess
import sys

import requests

_token = None


def _secret(name):
    return subprocess.run(
        ["gcloud", "secrets", "versions", "access", "latest",
         "--secret", name, "--project", "pipal-app"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def token():
    global _token
    if _token:
        return _token
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(_secret("spotify-client-id"), _secret("spotify-client-secret")),
    )
    resp.raise_for_status()
    _token = resp.json()["access_token"]
    return _token


def api(path, **params):
    resp = requests.get(
        f"https://api.spotify.com/v1/{path}",
        headers={"Authorization": f"Bearer {token()}"},
        params=params,
    )
    if not resp.ok:
        sys.exit(f"Spotify API error {resp.status_code}: {resp.text}")
    return resp.json()


def fmt_ms(ms):
    return f"{ms // 60000}:{ms % 60000 // 1000:02d}"


def cmd_search(args):
    # The search endpoint rejects page sizes above 10, so paginate.
    # The "next" field is unreliable; stop on an empty page instead.
    seen = set()
    offset = 0
    while offset < args.limit:
        data = api("search", q=args.query, type=args.type, limit=10,
                   offset=offset, market="SE")
        items = data[args.type + "s"]["items"]
        if not items:
            break
        for item in items:
            if item["id"] in seen:
                continue
            seen.add(item["id"])
            if args.type == "album":
                a = item
                artists = ", ".join(x["name"] for x in a["artists"])
                print(f'{a["id"]}  [{a["total_tracks"]:3d} tracks]  {a["name"]}  --  {artists}')
            else:
                t = item
                artists = ", ".join(x["name"] for x in t["artists"])
                print(f'{t["id"]}  {fmt_ms(t["duration_ms"])}  {t["name"]}  --  {artists}'
                      f'  (album: {t["album"]["name"]})')
        offset += 10


def cmd_album(args):
    a = api(f"albums/{args.album_id}", market="SE")
    print(f'ALBUM {a["id"]}  {a["name"]}  --  '
          + ", ".join(x["name"] for x in a["artists"]))
    items = a["tracks"]["items"]
    nxt = a["tracks"].get("next")
    while nxt:
        page = requests.get(nxt, headers={"Authorization": f"Bearer {token()}"}).json()
        items += page["items"]
        nxt = page.get("next")
    for t in items:
        print(f'  {t["track_number"]:3d}. {t["id"]}  {fmt_ms(t["duration_ms"])}  {t["name"]}')


def cmd_albums_by_artist(args):
    seen = set()
    offset = 0
    while offset < args.limit:
        data = api(f"artists/{args.artist_id}/albums", market="SE",
                   include_groups="album,appears_on", limit=50, offset=offset)
        if not data["items"]:
            break
        for a in data["items"]:
            if a["id"] in seen:
                continue
            seen.add(a["id"])
            artists = ", ".join(x["name"] for x in a["artists"])
            print(f'{a["id"]}  [{a["total_tracks"]:3d} tracks]  {a["name"]}  --  {artists}')
        offset += 50
        if not data.get("next"):
            break


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--type", default="album", choices=["album", "track"])
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("album")
    s.add_argument("album_id")
    s.set_defaults(func=cmd_album)

    s = sub.add_parser("albums-by-artist")
    s.add_argument("artist_id")
    s.add_argument("--limit", type=int, default=100)
    s.set_defaults(func=cmd_albums_by_artist)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
