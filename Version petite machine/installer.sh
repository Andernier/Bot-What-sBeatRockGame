#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -s)" != Darwin || "$(uname -m)" != x86_64 ]]; then
  echo 'Cet installateur cible macOS sur Intel.'
  exit 1
fi
if ! xcode-select -p >/dev/null 2>&1; then
  echo "Installez les outils Apple avec : xcode-select --install"
  echo 'Attendez la fin de leur installation, puis relancez ce script.'
  exit 1
fi
# Prefer an explicit Python 3.12 installation over Apple's toolchain Python.
PYTHON_BIN="${ROCKBOT_PYTHON:-python3.12}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo 'Python 3.12 manque. Suivez LIRE-MOI.md, puis rouvrez Terminal.'
  exit 1
fi
"$PYTHON_BIN" -c 'import sys; assert sys.version_info[:2] == (3,12), "Utilisez Python 3.12"'
if [[ ! -d .venv ]]; then "$PYTHON_BIN" -m venv .venv; fi
source .venv/bin/activate
python -m pip install --upgrade 'pip<26'
python -m pip install 'cmake==3.31.6' 'scikit-build-core==0.10.7' 'setuptools<81' wheel
python -m pip install -r requirements.txt
# Build locally for Monterey's SDK and Intel CPU; no Metal or newer Accelerate API.
CMAKE_GENERATOR='Unix Makefiles' \
CMAKE_BUILD_PARALLEL_LEVEL=2 \
MACOSX_DEPLOYMENT_TARGET=12.0 \
CMAKE_ARGS='-DGGML_METAL=OFF -DGGML_ACCELERATE=OFF -DGGML_OPENMP=OFF -DGGML_NATIVE=ON -DCMAKE_OSX_DEPLOYMENT_TARGET=12.0' \
python -m pip install --no-build-isolation --no-binary=llama-cpp-python 'llama-cpp-python==0.3.16'
mkdir -p models
model_path='models/Qwen3-0.6B-Q8_0.gguf'
if [[ ! -f "$model_path" ]]; then
  echo 'Téléchargement du modèle officiel Qwen (~640 Mo)…'
  curl --fail --location --retry 3 \
    'https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q8_0.gguf' \
    --output "${model_path}.part"
  python - "${model_path}.part" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
with p.open('rb') as f:
    if f.read(4) != b'GGUF' or p.stat().st_size < 500_000_000:
        raise SystemExit('Téléchargement du modèle incomplet ou invalide.')
PY
  mv "${model_path}.part" "$model_path"
fi
python -m unittest -v
printf '\nInstallation terminée. Testez : bash lancer.sh --check-model\n'
