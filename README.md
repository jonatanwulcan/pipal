# Pi Pal

A Raspberry Pi-based smart home controller designed for toddlers, letting them control things like music playback on Sonos speakers with simple keyboard presses.

## Deploy

Run from the repo root:

```bash
./scripts/deploy.sh
```

This copies `pipal.py` and the systemd service to `jonatan@dag.local`, then enables and starts the service (or restarts it if already installed).
