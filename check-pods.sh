#!/bin/bash

# Check pod status
kubectl get pods -n usenlease

# Get detailed information about the deployment
kubectl describe deployment usenlease-deployment -n usenlease

# Check pod logs for the first pod
POD=$(kubectl get pods -n usenlease -l app=usenlease-app -o jsonpath='{.items[0].metadata.name}')
if [ -n "$POD" ]; then
  echo "Logs for $POD:"
  kubectl logs $POD -n usenlease --tail=50
fi