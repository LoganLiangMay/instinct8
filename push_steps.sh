#!/bin/bash

# GitHub CLI Authentication and Push Script
# Run this after gh installation completes

echo "Step 1: Authenticate with GitHub"
gh auth login

echo -e "\nStep 2: Navigate to project directory"
cd /Applications/Projects/instinct8_2

echo -e "\nStep 3: Verify you're on the right branch with the right commit"
git log --oneline -n 1

echo -e "\nStep 4: Push to GitHub"
git push origin main

echo -e "\nStep 5: Verify push succeeded"
gh repo view LoganLiangMay/instinct8 --web

echo -e "\nDone! Your changes should now be on GitHub."