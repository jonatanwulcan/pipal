#!/usr/bin/env bash
set -euo pipefail

HOST="jonatan@dag.local"
REMOTE_DIR="/home/pi/pipal"
SERVICE_NAME="pipal"
SERVICE_FILE="systemd/pipal.service"

echo "Deploying to $HOST..."

ssh "$HOST" "mkdir -p $REMOTE_DIR/systemd"

scp pipal.py "$HOST:$REMOTE_DIR/pipal.py"
scp "$SERVICE_FILE" "$HOST:$REMOTE_DIR/$SERVICE_FILE"

ssh "$HOST" bash <<EOF
set -euo pipefail
sudo cp $REMOTE_DIR/$SERVICE_FILE /etc/systemd/system/$SERVICE_NAME.service
sudo systemctl daemon-reload

if systemctl is-enabled --quiet $SERVICE_NAME; then
  sudo systemctl restart $SERVICE_NAME
else
  sudo systemctl enable --now $SERVICE_NAME
fi

echo "Status:"
sudo systemctl status $SERVICE_NAME --no-pager
EOF

echo "Done."
