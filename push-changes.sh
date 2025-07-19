#!/bin/bash

# Add all changes
git add .

# Commit changes
git commit -m "Fix deployment probes to use TCP socket instead of HTTP"

# Push to origin (correct spelling)
git push origin master