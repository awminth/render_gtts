#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# FFmpeg သွင်းခြင်း
apt-get update && apt-get install -y ffmpeg