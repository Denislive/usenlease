#!/bin/bash

# List all resources managed by ArgoCD
kubectl exec -n argocd deploy/argocd-server -- argocd app resources usenlease-app