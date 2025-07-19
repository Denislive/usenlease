#!/bin/bash

# Apply namespace first
kubectl apply -f k8s/usenlease-namespace.yaml --validate=false

# Apply config and secrets
kubectl apply -f k8s/usenlease-config.yaml --validate=false
kubectl apply -f k8s/usenlease-secrets.yaml --validate=false

# Apply Redis resources
kubectl apply -f k8s/redis-deployment.yaml --validate=false
kubectl apply -f k8s/redis-service.yaml --validate=false

# Apply main application resources
kubectl apply -f k8s/usenlease-deployment.yaml --validate=false
kubectl apply -f k8s/usenlease-service.yaml --validate=false
kubectl apply -f k8s/usenlease-ingress.yaml --validate=false

# Apply HPA if needed
kubectl apply -f k8s/usenlease-hpa.yaml --validate=false

echo "Deployment completed with validation disabled"