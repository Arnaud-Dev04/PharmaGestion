#!/bin/bash
# build.sh — Script de build Flutter Web pour Vercel
# Arrête immédiatement en cas d'erreur
set -e
set -x   # Active le mode verbeux pour voir chaque commande dans les logs

echo "=========================================="
echo " PharmaGestion — Build Flutter Web"
echo "=========================================="

# ── 1. Téléchargement Flutter SDK ────────────────────────────────────────────
FLUTTER_VERSION="3.24.5"   # Version LTS stable

if [ ! -d "flutter" ]; then
  echo "[1/4] Téléchargement Flutter $FLUTTER_VERSION..."
  # Utilise un tarball (plus rapide que git clone complet)
  curl -fsSL "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_${FLUTTER_VERSION}-stable.tar.xz" \
    -o flutter.tar.xz
  tar xf flutter.tar.xz
  rm flutter.tar.xz
  echo "Flutter SDK extrait."
else
  echo "[1/4] Flutter SDK déjà présent."
fi

export PATH="$PATH:$(pwd)/flutter/bin"

# ── 2. Configuration Flutter ──────────────────────────────────────────────────
echo "[2/4] Configuration Flutter..."
flutter config --no-analytics
flutter config --enable-web
flutter --version

# ── 3. Dépendances ────────────────────────────────────────────────────────────
echo "[3/4] Installation des dépendances..."
cd frontend1
flutter pub get
cd ..

# ── 4. Build Web ──────────────────────────────────────────────────────────────
echo "[4/4] Build Flutter Web (canvaskit)..."
flutter build web --release --web-renderer canvaskit -C frontend1

echo "=========================================="
echo " Build terminé avec succès !"
echo " Output: frontend1/build/web"
echo "=========================================="
