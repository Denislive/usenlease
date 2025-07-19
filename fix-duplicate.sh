#!/bin/bash

# Copy the fixed deployment over the original
cp k8s/usenlease-deployment-fixed.yaml k8s/usenlease-deployment.yaml

# Remove the duplicate file
rm k8s/usenlease-deployment-fixed.yaml

# Add and commit changes
git add k8s/
git commit -m "Remove duplicate deployment file"

# Apply the updated deployment
kubectl apply -f k8s/usenlease-deployment.yaml --validate=false