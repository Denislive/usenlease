#!/bin/bash

# Update kubeconfig to connect to the EKS cluster
aws eks update-kubeconfig --name usenlease-eks --region us-east-1

# Verify connection
kubectl get nodes