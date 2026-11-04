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
  -> GitHub Actions builds the demo app image and pushes it to GHCR
  -> the CI step updates the image tag in k8s/overlays/prod
  -> Argo CD (running in kind) syncs the prod overlay into the cluster
  -> the demo app serves traffic on http://localhost:8080
```

- `app/` — the demo app: a dependency-free Python HTTP server that
  reports its version from the `APP_VERSION` environment variable.
- `k8s/base/` — the shared Deployment and Service.
- `k8s/overlays/dev/` — 1 replica, version `dev`.
- `k8s/overlays/prod/` — 2 replicas, version set by CI on each push.
- `.github/workflows/ci.yml` — builds and pushes the image, then updates
  the prod overlay image tag and commits it back.
- `argocd/application.yaml` — the Argo CD Application that tracks the
  prod overlay (apply it after installing Argo CD in your cluster).
- `scripts/kind-bootstrap.sh` — creates the kind cluster, installs Argo
  CD, and applies the Application.

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

Day 1 of the build-out (4 Nov 2026): README, demo app, Kustomize
manifests, CI workflow, Argo CD Application and the kind bootstrap
script. Next steps: verify the full loop on a real kind cluster and add
a CI job that validates the manifests with `kustomize build`.
