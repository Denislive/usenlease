#!/bin/bash

# Apply the updated deployment with TCP probes
kubectl apply -f k8s/usenlease-deployment.yaml --validate=false

# Delete any failed pods to force recreation
kubectl get pods -n usenlease -l app=usenlease-app | grep -v Running | awk '{print $1}' | xargs -r kubectl delete pod -n usenlease

# Wait for rollout
echo "Waiting for deployment rollout..."
kubectl rollout status deployment/usenlease-deployment -n usenlease --timeout=120s