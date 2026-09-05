# Pi Pal

A Raspberry Pi-based smart home controller designed for toddlers, letting them control things like music playback on Sonos speakers with simple keyboard presses.

## Setup

### Plejd credentials

Copy the example credentials file and fill in your details:

```bash
cp plejd_credentials.json.example plejd_credentials.json
```

Edit `plejd_credentials.json` with your Plejd account email, password, and site ID. The file is gitignored and will be copied to the Pi on deploy. Your site ID can be found in the Plejd app under Settings → Installation.

### FaceTime credentials

The 6-key cluster above the arrow keys (Insert, Home, Page Up, Delete, End, Page Down) each send a trigger email to the iPad's own iCloud account. A Shortcuts personal automation on the iPad watches for a specific subject line and starts a FaceTime call. Each key maps to a contact name (see `FACETIME_ENTRIES` in `pipal.py`); `facetime_credentials.json` maps each contact name to its subject line, keeping the physical keyboard layout and the FaceTime secrets independent of each other.

```bash
cp facetime_credentials.json.example facetime_credentials.json
```

Edit `facetime_credentials.json`:
- `username` / `password`: the iPad's iCloud address and an app-specific password (generate one at [appleid.apple.com](https://appleid.apple.com), since iCloud SMTP won't accept the account's real password).
- `contacts`: a high-entropy random subject per contact name, so only this device can trigger a call. Generate each with:
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

On the iPad, create one Shortcuts personal automation per key: trigger on "Email", filtered to the matching subject, with "Ask Before Running" turned off, running a shortcut that FaceTimes the intended family member.

This file is gitignored and copied to the Pi on deploy.

## Deploy

Run from the repo root:

```bash
./scripts/deploy.sh
```

This copies `pipal.py` and the systemd service to `jonatan@dag.local`, then enables and starts the service (or restarts it if already installed).

## Logs

```bash
./scripts/logs.sh        # last 100 lines
./scripts/logs.sh 50     # last 50 lines
```
