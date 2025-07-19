#!/bin/bash

# Configure git merge strategy
git config pull.rebase false

# Pull changes from remote
git pull

# Push your changes
git push origin master