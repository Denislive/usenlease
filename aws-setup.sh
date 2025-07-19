#!/bin/bash

echo "Please enter your AWS credentials when prompted:"
aws configure

# After configuring AWS credentials, update kubeconfig
echo "Updating kubeconfig to connect to EKS cluster..."
aws eks update-kubeconfig --name usenlease-eks --region us-east-1

# Verify connection
echo "Verifying connection to EKS cluster..."
kubectl get nodes