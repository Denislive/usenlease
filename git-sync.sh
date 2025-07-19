#!/bin/bash

# Configure git merge strategy
git config pull.rebase false

# Stash local changes
git stash

# Pull remote changes
git pull origin master

# Apply stashed changes
git stash pop

# Add all changes
git add .

# Commit changes
git commit -m "Update deployment configuration and cleanup scripts"

# Push changes
git push origin master