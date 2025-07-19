#!/bin/bash

# Delete the old deployment
kubectl delete deployment usenlease-deployment -n usenlease

# Apply the renamed deployment
kubectl apply -f k8s/usenlease-deployment-renamed.yaml --validate=false

# Apply the updated HPA
kubectl apply -f k8s/usenlease-hpa.yaml --validate=false

# Remove the old deployment file
rm k8s/usenlease-deployment.yaml

# Rename the new file to the standard name
mv k8s/usenlease-deployment-renamed.yaml k8s/usenlease-deployment.yaml

# Commit changes
git add k8s/
git commit -m "Rename deployment to fix duplicate resource issue"