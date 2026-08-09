#!/bin/bash
set -e

gcloud run deploy spotify \
  --source functions/spotify \
  --region europe-north1 \
  --service-account spotify-runner@pipal-app.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --project pipal-app
