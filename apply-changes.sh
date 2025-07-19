#!/bin/bash

# Apply the updated deployment and HPA
kubectl apply -f k8s/usenlease-deployment.yaml --validate=false
kubectl apply -f k8s/usenlease-hpa.yaml --validate=false

# Check deployment status
echo "Checking deployment status..."
kubectl rollout status deployment/usenlease-deployment -n usenlease