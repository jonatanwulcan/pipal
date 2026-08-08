#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../pwa"
firebase deploy --only hosting
