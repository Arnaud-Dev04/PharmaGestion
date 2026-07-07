#!/bin/bash
# build.sh — Script de build Flutter Web pour Vercel
set -e
set -x

echo "=========================================="
echo " PharmaGestion — Build Flutter Web"
echo "=========================================="

# ── Fix git ownership (Vercel tourne en root) ─────────────────────────────────
git config --global --add safe.directory '*'

# ── 1. Téléchargement Flutter SDK ────────────────────────────────────────────
FLUTTER_VERSION="3.24.5"
FLUTTER_DIR="$(pwd)/flutter"

if [ ! -d "$FLUTTER_DIR" ]; then
  echo "[1/4] Téléchargement Flutter $FLUTTER_VERSION..."
  curl -fsSL \
    "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_${FLUTTER_VERSION}-stable.tar.xz" \
    -o flutter.tar.xz
  tar xf flutter.tar.xz
  rm flutter.tar.xz
  echo "Flutter SDK extrait."
else
  echo "[1/4] Flutter SDK déjà en cache."
fi

export PATH="$PATH:$FLUTTER_DIR/bin"

# ── 2. Configuration Flutter ──────────────────────────────────────────────────
echo "[2/4] Configuration Flutter..."
git config --global --add safe.directory "$FLUTTER_DIR"
flutter config --no-analytics
flutter config --enable-web
flutter --version

# ── 3. Dépendances ────────────────────────────────────────────────────────────
echo "[3/4] Installation des dépendances..."
flutter pub get --directory=frontend1

# ── 4. Build Web ──────────────────────────────────────────────────────────────
echo "[4/4] Build Flutter Web (canvaskit)..."
flutter build web --release --web-renderer canvaskit -C frontend1

echo "=========================================="
echo " Build terminé ! Output: frontend1/build/web"
echo "=========================================="
