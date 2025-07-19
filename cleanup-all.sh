#!/bin/bash

# Apply the updated deployment
kubectl apply -f k8s/usenlease-deployment.yaml --validate=false

# Delete old ReplicaSets with 0 replicas
kubectl delete rs $(kubectl get rs -n usenlease -l app=usenlease-app --no-headers | grep "0         0         0" | awk '{print $1}') -n usenlease