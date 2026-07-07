#!/bin/bash
# build.sh — Script de build Flutter Web pour Vercel
set -e

# Installe Flutter si absent
if [ ! -d flutter ]; then
  git clone https://github.com/flutter/flutter.git --depth 1 -b stable
fi

flutter/bin/flutter config --no-analytics
flutter/bin/flutter pub get --directory=frontend1
flutter/bin/flutter build web --release --web-renderer canvaskit -C frontend1
