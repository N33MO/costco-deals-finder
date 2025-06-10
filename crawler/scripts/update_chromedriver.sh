#!/usr/bin/env bash
# update_chromedriver.sh — simplified
# -----------------------------------------------------------
# Usage: ./update_chromedriver.sh <direct‑download‑URL>
# Downloads the specified mac‑arm64 ChromeDriver zip, replaces
# any existing driver, and self‑signs the binary to satisfy
# macOS Gatekeeper.
# link: https://googlechromelabs.github.io/chrome-for-testing/
# -----------------------------------------------------------

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <chromedriver-zip-url>"
  echo "Check the link: https://googlechromelabs.github.io/chrome-for-testing/"
  echo
  echo "→ Checking installed Google Chrome version..."
  if command -v google-chrome >/dev/null 2>&1; then
    google-chrome --version
  elif [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version
  else
    echo "⚠️  google-chrome command not found. Please ensure Chrome is installed and in your PATH."
  fi
  exit 1
fi

URL="$1"
ARCH="mac-arm64"
TARGET_PARENT="$(dirname "$0")"
TARGET_DIR="${TARGET_PARENT}/chromedriver-${ARCH}"
BIN="${TARGET_DIR}/chromedriver"

echo "→ Removing any existing ChromeDriver at ${TARGET_DIR}"
rm -rf "${TARGET_DIR}"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

ZIP="${TMP}/chromedriver.zip"
echo "→ Downloading ChromeDriver from ${URL}"
curl -#fSL "${URL}" -o "${ZIP}"

echo "→ Extracting ChromeDriver..."
unzip -qo "${ZIP}" -d "${TARGET_PARENT}"

echo "→ Fixing permissions and Gatekeeper flags..."
chmod +x "${BIN}"
xattr -d com.apple.quarantine "${BIN}" 2>/dev/null || true
codesign --force --deep --sign - "${BIN}"

echo "✅  ChromeDriver is ready at ${BIN}"