#!/bin/bash

# Deploy to GitHub Script
# This script helps you deploy your NLP to SQL application to GitHub

echo "================================================"
echo "  NLP to SQL - GitHub Deployment Helper"
echo "================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed."
    echo "Please install Git first: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Check if already a git repository
if [ -d .git ]; then
    echo "⚠️  This directory is already a Git repository."
    echo ""
    read -p "Do you want to continue? (y/n): " continue_choice
    if [ "$continue_choice" != "y" ]; then
        echo "Exiting..."
        exit 0
    fi
else
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
fi

# Check Git configuration
echo "🔧 Checking Git configuration..."
git_name=$(git config user.name)
git_email=$(git config user.email)

if [ -z "$git_name" ] || [ -z "$git_email" ]; then
    echo "⚠️  Git user not configured."
    echo ""
    read -p "Enter your name: " user_name
    read -p "Enter your email: " user_email

    git config user.name "$user_name"
    git config user.email "$user_email"

    echo "✅ Git user configured"
else
    echo "✅ Git user: $git_name <$git_email>"
fi
echo ""

# Check for .env file
if [ -f .env ]; then
    echo "🔐 .env file found"
    if grep -q ".env" .gitignore; then
        echo "✅ .env is in .gitignore (good!)"
    else
        echo "⚠️  WARNING: .env is NOT in .gitignore!"
        echo "Adding .env to .gitignore..."
        echo ".env" >> .gitignore
        echo "✅ .env added to .gitignore"
    fi
else
    echo "ℹ️  No .env file found (this is okay if using .env.example)"
fi
echo ""

# Show files to be committed
echo "📋 Files to be committed:"
git status --short
echo ""

read -p "Continue with commit? (y/n): " commit_choice
if [ "$commit_choice" != "y" ]; then
    echo "Exiting without committing..."
    exit 0
fi

# Stage all files
echo "📦 Staging files..."
git add .
echo "✅ Files staged"
echo ""

# Commit
read -p "Enter commit message (default: 'Initial commit'): " commit_msg
commit_msg=${commit_msg:-"Initial commit: NLP to SQL Chat Application with professional reports"}

echo "💾 Creating commit..."
git commit -m "$commit_msg"
echo "✅ Commit created"
echo ""

# Check if remote exists
if git remote get-url origin &> /dev/null; then
    echo "✅ Remote 'origin' already exists"
    remote_url=$(git remote get-url origin)
    echo "   URL: $remote_url"
    echo ""

    read -p "Push to this remote? (y/n): " push_choice
    if [ "$push_choice" == "y" ]; then
        echo "🚀 Pushing to GitHub..."
        git push -u origin main || git push -u origin master
        echo ""
        echo "✅ Code pushed to GitHub!"
    fi
else
    echo "📡 No remote repository configured."
    echo ""
    echo "Next steps:"
    echo "1. Create a repository on GitHub.com"
    echo "2. Run these commands:"
    echo ""
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
fi

echo ""
echo "================================================"
echo "  Deployment Complete!"
echo "================================================"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo ""
