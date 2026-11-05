# gitops-k8s-pipeline

A free, end-to-end GitOps CI/CD demo: a tiny demo app, built by GitHub
Actions, published to GitHub Container Registry (GHCR), and deployed to a
local Kubernetes cluster (kind) by Argo CD using Kustomize overlays.

No live dashboard is claimed here — this is a local demo you run yourself.
Everything is free: GitHub Actions, GHCR, kind, Kustomize and Argo CD all
have free tiers or are open source, and no cloud account is needed.

## How it works

```
push to main
  -> GitHub Actions runs the app tests and builds both Kustomize overlays
  -> it builds the demo app image and pushes it to GHCR
  -> the CI step updates the image tag in k8s/overlays/prod
  -> Argo CD (running in kind) syncs the prod overlay into the cluster
  -> the demo app serves traffic on http://localhost:8080
```

- `app/` — the demo app: a dependency-free Python HTTP server that
  reports its version from the `APP_VERSION` environment variable.
- `tests/` — stdlib-only tests for the demo app (`/`, `/healthz`,
  version reporting). Run them with `python3 -m unittest discover -s tests -v`.
- `k8s/base/` — the shared Deployment and Service.
- `k8s/overlays/dev/` — 1 replica, version `dev`.
- `k8s/overlays/prod/` — 2 replicas, version set by CI on each push.
- `.github/workflows/ci.yml` — tests the app, validates the overlays with
  `kustomize build`, builds and pushes the image, then updates the prod
  overlay image tag and commits it back.
- `.github/workflows/validate.yaml` — validates the manifests (YAML parse
  + `kustomize build` of both overlays) whenever they change. It never
  builds, pushes or commits, so the CI bot's own overlay updates cannot
  trigger a loop through it.
- `argocd/application.yaml` — the Argo CD Application that tracks the
  prod overlay (apply it after installing Argo CD in your cluster).
- `scripts/kind-bootstrap.sh` — creates the kind cluster, installs Argo
  CD, and applies the Application.
- `scripts/verify.sh` — local pre-push check: app tests, YAML parse, and
  `kustomize build` of both overlays when kustomize is installed
  (`bash scripts/verify.sh`).

## Quickstart (local demo)

Prerequisites: Docker, kind, kubectl, and the Argo CD CLI optional.

```bash
# 1. Create the cluster and install Argo CD
bash scripts/kind-bootstrap.sh

# 2. Port-forward the demo app once Argo CD has synced it
kubectl -n demo port-forward svc/demo 8080:80

# 3. Open http://localhost:8080 — it shows the running app version
```

To try a new version locally without CI:

```bash
docker build -t demo:local app/
kind load docker-image demo:local --name gitops-demo
kubectl -n demo set image deployment/demo demo=demo:local
```

## Repository layout

See the directories listed above. Every manifest is plain YAML that
`kubectl apply -k` understands — no templating engine is required.

## Status

Day 2 of the build-out (5 Nov 2026): the CI pipeline now works end to
end. The first CI run failed because the repository's workflow
permissions were read-only, so the GHCR push was denied; setting them to
read and write fixed it. The next run passed in 26s — tests and overlay
builds green, image pushed to GHCR, and the bot updated the prod overlay
to the new image tag. Manifest edits are now validated by a separate
workflow, the Deployment has readiness/liveness probes and resource
limits, and the overlays use the current `labels` field instead of the
deprecated `commonLabels`.

Next steps: verify the full loop on a real kind cluster (create it with
`scripts/kind-bootstrap.sh`, then confirm Argo CD syncs the prod overlay
and the app answers on http://localhost:8080).
