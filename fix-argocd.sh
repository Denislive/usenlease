#!/bin/bash

# Refresh ArgoCD application
kubectl patch application usenlease-app -n argocd --type merge -p '{"spec":{"source":{"path":"k8s"}}}'

# Force sync with pruning
kubectl exec -n argocd deploy/argocd-server -- argocd app sync usenlease-app --prune

# Check application status
kubectl get application usenlease-app -n argocd -o jsonpath='{.status.sync.status}'