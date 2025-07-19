#!/bin/bash

# Apply the fixed deployment
kubectl apply -f k8s/usenlease-deployment-fixed.yaml --validate=false

# Force rollout restart to ensure changes are applied
kubectl rollout restart deployment/usenlease-deployment -n usenlease

# Wait for rollout
echo "Waiting for deployment rollout..."
kubectl rollout status deployment/usenlease-deployment -n usenlease --timeout=180s