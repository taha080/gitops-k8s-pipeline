#!/usr/bin/env bash
# Create a local kind cluster, install Argo CD, and apply the demo Application.
# Requires: docker, kind, kubectl. Safe to re-run: existing cluster is reused.
set -euo pipefail

CLUSTER=gitops-demo

if ! kind get clusters | grep -qx "$CLUSTER"; then
  kind create cluster --name "$CLUSTER"
fi

kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd wait --for=condition=available deployment/argocd-server --timeout=300s

kubectl apply -f argocd/application.yaml
echo "Done. Port-forward the app with: kubectl -n demo port-forward svc/demo 8080:80"
