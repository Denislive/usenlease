#!/bin/bash

# Get the list of old ReplicaSets to delete
OLD_RS=$(kubectl get rs -n usenlease -l app=usenlease-app --no-headers | grep "0         0         0" | awk '{print $1}')

# Delete each ReplicaSet one by one
for rs in $OLD_RS; do
  echo "Deleting $rs"
  kubectl delete rs $rs -n usenlease
done