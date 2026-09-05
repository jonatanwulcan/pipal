#!/usr/bin/env bash
set -euo pipefail

HOST="jonatan@dag.local"
SERVICE_NAME="pipal"
SERVICE_FILE="systemd/pipal.service"

echo "Deploying to $HOST..."

REMOTE_HOME=$(ssh "$HOST" 'echo $HOME')
REMOTE_DIR="$REMOTE_HOME/pipal"

ssh "$HOST" "mkdir -p $REMOTE_DIR/systemd"

scp pipal.py "$HOST:$REMOTE_DIR/pipal.py"
scp plejd.py "$HOST:$REMOTE_DIR/plejd.py"
scp sonos.py "$HOST:$REMOTE_DIR/sonos.py"
scp stories.py "$HOST:$REMOTE_DIR/stories.py"
scp facetime.py "$HOST:$REMOTE_DIR/facetime.py"
scp "$SERVICE_FILE" "$HOST:$REMOTE_DIR/$SERVICE_FILE"
scp requirements.txt "$HOST:$REMOTE_DIR/requirements.txt"
scp plejd_credentials.json "$HOST:$REMOTE_DIR/plejd_credentials.json"
scp facetime_credentials.json "$HOST:$REMOTE_DIR/facetime_credentials.json"

ssh "$HOST" "sed -i 's|/home/pi/pipal|$REMOTE_DIR|g' $REMOTE_DIR/$SERVICE_FILE"

ssh "$HOST" bash <<EOF
set -euo pipefail

if ! dpkg -s python3-venv &>/dev/null; then
  sudo apt-get install -y python3-venv
fi

if [ ! -d $REMOTE_DIR/venv ]; then
  python3 -m venv $REMOTE_DIR/venv
fi

$REMOTE_DIR/venv/bin/pip install -q -r $REMOTE_DIR/requirements.txt

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
