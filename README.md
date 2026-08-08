# Pi Pal

A Raspberry Pi-based smart home controller designed for toddlers, letting them control things like music playback on Sonos speakers with simple keyboard presses.

## Setup

### Plejd credentials

Copy the example credentials file and fill in your details:

```bash
cp plejd_credentials.json.example plejd_credentials.json
```

Edit `plejd_credentials.json` with your Plejd account email, password, and site ID. The file is gitignored and will be copied to the Pi on deploy. Your site ID can be found in the Plejd app under Settings → Installation.

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
