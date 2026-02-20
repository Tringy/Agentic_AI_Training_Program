#!/bin/bash
# Deployment script for AI Training projects
# Supports Railway (backend) and Vercel (frontend)

set -e  # Exit on error

PROJECT_NAME=$1
BACKEND_PATH=$2
FRONTEND_PATH=$3

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: ./deploy.sh <project-name> [backend-path] [frontend-path]"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh my-agent ./python"
    echo "  ./deploy.sh my-app ./backend ./frontend"
    echo ""
    exit 1
fi

echo "🚀 Deploying: $PROJECT_NAME"
echo "=============================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI not found"
    echo "   Install: npm install -g @railway/cli"
    echo "   Or deploy manually at https://railway.app"
    echo ""
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI not found"
    echo "   Install: npm install -g vercel"
    echo "   Or deploy manually at https://vercel.com"
    echo ""
fi

# Deploy backend
if [ ! -z "$BACKEND_PATH" ]; then
    if [ -d "$BACKEND_PATH" ]; then
        echo "Deploying backend: $BACKEND_PATH"
        echo "---"

        cd "$BACKEND_PATH"

        if command -v railway &> /dev/null; then
            # Check if already linked
            if [ ! -f "railway.toml" ] && [ ! -f ".railway" ]; then
                echo "Initializing Railway project..."
                railway init
            fi

            # Deploy
            echo "Deploying to Railway..."
            railway up

            # Get URL
            BACKEND_URL=$(railway status | grep "URL" | awk '{print $2}')
            if [ ! -z "$BACKEND_URL" ]; then
                echo "✅ Backend deployed: $BACKEND_URL"
            else
                echo "✅ Backend deployed (check Railway dashboard for URL)"
            fi
        else
            echo "⚠️  Skipping backend deployment (Railway CLI not found)"
        fi

        cd - > /dev/null
        echo ""
    else
        echo "⚠️  Backend path not found: $BACKEND_PATH"
        echo ""
    fi
fi

# Deploy frontend
if [ ! -z "$FRONTEND_PATH" ]; then
    if [ -d "$FRONTEND_PATH" ]; then
        echo "Deploying frontend: $FRONTEND_PATH"
        echo "---"

        cd "$FRONTEND_PATH"

        if command -v vercel &> /dev/null; then
            # Deploy to production
            echo "Deploying to Vercel..."
            vercel --prod --yes

            echo "✅ Frontend deployed"
        else
            echo "⚠️  Skipping frontend deployment (Vercel CLI not found)"
        fi

        cd - > /dev/null
        echo ""
    else
        echo "⚠️  Frontend path not found: $FRONTEND_PATH"
        echo ""
    fi
fi

# If no paths provided, try to auto-detect
if [ -z "$BACKEND_PATH" ] && [ -z "$FRONTEND_PATH" ]; then
    echo "Auto-detecting project structure..."
    echo ""

    # Check for Python backend
    if [ -f "main.py" ] || [ -f "app.py" ]; then
        echo "Detected Python backend in current directory"

        if command -v railway &> /dev/null; then
            railway init || true
            railway up
            echo "✅ Backend deployed"
        fi
    fi

    # Check for Node.js frontend
    if [ -f "package.json" ]; then
        echo "Detected Node.js project in current directory"

        if command -v vercel &> /dev/null; then
            vercel --prod --yes
            echo "✅ Frontend deployed"
        fi
    fi
fi

echo ""
echo "=============================="
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Check deployment URLs above"
echo "2. Set environment variables in Railway/Vercel dashboard"
echo "3. Test deployed endpoints"
echo "4. Update README with deployment URLs"
echo ""
