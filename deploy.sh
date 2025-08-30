#!/bin/bash

# FormulaHub API Deployment Script for Cloudflare Workers

echo "🚀 Deploying FormulaHub API to Cloudflare Workers..."

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI is not installed. Please install it first:"
    echo "npm install -g wrangler"
    exit 1
fi

# Check if user is logged in to Cloudflare
if ! wrangler whoami &> /dev/null; then
    echo "❌ Not logged in to Cloudflare. Please run:"
    echo "wrangler login"
    exit 1
fi

# Deploy to staging first
echo "📦 Deploying to staging environment..."
wrangler deploy --env staging

if [ $? -eq 0 ]; then
    echo "✅ Staging deployment successful!"
    
    # Ask if user wants to deploy to production
    read -p "🤔 Deploy to production? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Deploying to production..."
        wrangler deploy --env production
        if [ $? -eq 0 ]; then
            echo "✅ Production deployment successful!"
            echo "🌐 Your API is now live at: https://formulahub-api.your-subdomain.workers.dev"
        else
            echo "❌ Production deployment failed!"
        fi
    fi
else
    echo "❌ Staging deployment failed!"
    exit 1
fi

echo "🎉 Deployment process completed!"
