#!/usr/bin/env bash
# Local pre-push check for gitops-k8s-pipeline: run the app tests, check
# every manifest parses as YAML, and build both Kustomize overlays when
# kustomize is installed (skipped with a note when it is not).
# Usage: bash scripts/verify.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== demo app tests =="
python3 -m unittest discover -s tests -v

echo "== manifests parse as YAML =="
python3 -c "import glob, yaml; [yaml.safe_load(open(f)) for f in glob.glob('k8s/**/*.yaml', recursive=True)]; print('manifests OK')"

if command -v kustomize >/dev/null 2>&1; then
  echo "== kustomize build overlays =="
  kustomize build k8s/overlays/dev > /dev/null
  kustomize build k8s/overlays/prod > /dev/null
  echo "overlays OK"
else
  echo "== kustomize not installed, overlay build skipped =="
  echo "Install it from https://kubectl.docs.kubernetes.io/installation/kustomize/ to check overlays locally."
fi

echo "All local checks passed."
