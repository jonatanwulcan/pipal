#!/usr/bin/env bash
set -euo pipefail

HOST="jonatan@dag.local"
LINES="${1:-100}"

ssh "$HOST" "journalctl -u pipal -n $LINES --no-pager"
