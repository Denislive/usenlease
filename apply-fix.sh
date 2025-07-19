#!/bin/bash

# Apply the updated deployment
kubectl apply -f k8s/usenlease-deployment.yaml --validate=false

# Wait for rollout
kubectl rollout status deployment/usenlease-deployment -n usenlease --timeout=120s

# Check pod status
kubectl get pods -n usenlease