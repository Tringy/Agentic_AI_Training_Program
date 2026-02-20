#!/bin/bash

# ============================================================================
# Agentic AI Training - Environment Setup Verification Script
# ============================================================================
# Usage: ./scripts/verify-setup.sh [python|typescript|all]
# Default: all
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
    echo ""
}

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}○${NC} $1"
    ((WARN++))
}

# ============================================================================
# Python Checks
# ============================================================================
check_python() {
    print_header "Python Environment"

    # Check Python version
    if command -v python3 &> /dev/null; then
        PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
        PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)

        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
            check_pass "Python $PY_VERSION"
        else
            check_fail "Python $PY_VERSION (need 3.10+)"
        fi
    else
        check_fail "Python not found"
    fi

    # Check pip
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version | awk '{print $2}')
        check_pass "pip $PIP_VERSION"
    else
        check_fail "pip not found"
    fi

    # Check virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        check_pass "Virtual environment active: $(basename $VIRTUAL_ENV)"
    else
        check_warn "No virtual environment active (recommended)"
    fi

    # Check Python packages
    echo ""
    echo "Python Packages:"

    PACKAGES=("openai" "anthropic" "fastapi" "chromadb" "pydantic")
    for pkg in "${PACKAGES[@]}"; do
        if python3 -c "import $pkg" 2>/dev/null; then
            VERSION=$(python3 -c "import $pkg; print(getattr($pkg, '__version__', 'installed'))" 2>/dev/null || echo "installed")
            check_pass "$pkg ($VERSION)"
        else
            check_fail "$pkg not installed"
        fi
    done

    # Optional packages
    OPTIONAL_PACKAGES=("langchain" "tiktoken" "google.generativeai")
    for pkg in "${OPTIONAL_PACKAGES[@]}"; do
        if python3 -c "import $pkg" 2>/dev/null; then
            check_pass "$pkg (optional)"
        else
            check_warn "$pkg not installed (optional)"
        fi
    done
}

# ============================================================================
# TypeScript/Node.js Checks
# ============================================================================
check_typescript() {
    print_header "TypeScript/Node.js Environment"

    # Check Node.js version
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)

        if [ "$NODE_MAJOR" -ge 18 ]; then
            check_pass "Node.js $NODE_VERSION"
        else
            check_fail "Node.js $NODE_VERSION (need 18+)"
        fi
    else
        check_fail "Node.js not found"
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        check_pass "npm $NPM_VERSION"
    else
        check_fail "npm not found"
    fi

    # Check TypeScript
    if command -v npx &> /dev/null && npx tsc --version &> /dev/null; then
        TSC_VERSION=$(npx tsc --version | awk '{print $2}')
        check_pass "TypeScript $TSC_VERSION"
    else
        check_warn "TypeScript not installed globally (will use local)"
    fi

    # Check if package.json exists and has dependencies
    if [ -f "package.json" ]; then
        check_pass "package.json found"

        # Check if node_modules exists
        if [ -d "node_modules" ]; then
            check_pass "node_modules installed"
        else
            check_warn "node_modules not found (run 'npm install')"
        fi
    else
        check_warn "package.json not found in current directory"
    fi

    # Check key packages in node_modules
    echo ""
    echo "Node.js Packages:"

    PACKAGES=("@anthropic-ai/sdk" "openai" "hono" "zod")
    for pkg in "${PACKAGES[@]}"; do
        if [ -d "node_modules/$pkg" ]; then
            VERSION=$(node -e "console.log(require('$pkg/package.json').version)" 2>/dev/null || echo "installed")
            check_pass "$pkg ($VERSION)"
        else
            check_warn "$pkg not installed locally"
        fi
    done
}

# ============================================================================
# API Keys Check
# ============================================================================
check_api_keys() {
    print_header "API Keys"

    # Required (at least one)
    HAS_KEY=false

    if [ -n "$ANTHROPIC_API_KEY" ]; then
        check_pass "ANTHROPIC_API_KEY is set"
        HAS_KEY=true
    else
        check_warn "ANTHROPIC_API_KEY not set"
    fi

    if [ -n "$OPENAI_API_KEY" ]; then
        check_pass "OPENAI_API_KEY is set"
        HAS_KEY=true
    else
        check_warn "OPENAI_API_KEY not set"
    fi

    # Optional
    if [ -n "$GOOGLE_API_KEY" ]; then
        check_pass "GOOGLE_API_KEY is set"
        HAS_KEY=true
    else
        check_warn "GOOGLE_API_KEY not set (optional)"
    fi

    if [ -n "$GROQ_API_KEY" ]; then
        check_pass "GROQ_API_KEY is set (free tier)"
        HAS_KEY=true
    else
        check_warn "GROQ_API_KEY not set (optional, free tier available)"
    fi

    if [ "$HAS_KEY" = false ]; then
        check_fail "No LLM API key found! Set at least one API key."
    fi
}

# ============================================================================
# Common Tools Check
# ============================================================================
check_common_tools() {
    print_header "Common Tools"

    # Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | awk '{print $3}')
        check_pass "git $GIT_VERSION"
    else
        check_fail "git not found"
    fi

    # curl
    if command -v curl &> /dev/null; then
        check_pass "curl"
    else
        check_warn "curl not found"
    fi

    # Deployment CLIs (optional)
    echo ""
    echo "Deployment Tools (optional):"

    if command -v vercel &> /dev/null; then
        check_pass "vercel CLI"
    else
        check_warn "vercel CLI not installed"
    fi

    if command -v railway &> /dev/null; then
        check_pass "railway CLI"
    else
        check_warn "railway CLI not installed"
    fi
}

# ============================================================================
# Summary
# ============================================================================
print_summary() {
    print_header "Summary"

    echo -e "${GREEN}Passed:${NC} $PASS"
    echo -e "${RED}Failed:${NC} $FAIL"
    echo -e "${YELLOW}Warnings:${NC} $WARN"
    echo ""

    if [ $FAIL -eq 0 ]; then
        echo -e "${GREEN}============================================${NC}"
        echo -e "${GREEN}  All required checks passed! Ready to go.  ${NC}"
        echo -e "${GREEN}============================================${NC}"
        exit 0
    else
        echo -e "${RED}============================================${NC}"
        echo -e "${RED}  Some checks failed. Please fix before    ${NC}"
        echo -e "${RED}  continuing with the training.            ${NC}"
        echo -e "${RED}============================================${NC}"
        exit 1
    fi
}

# ============================================================================
# Main
# ============================================================================
main() {
    echo ""
    echo "============================================"
    echo "  Agentic AI Training - Setup Verification  "
    echo "============================================"

    MODE=${1:-all}

    case $MODE in
        python)
            check_python
            check_api_keys
            check_common_tools
            ;;
        typescript|ts)
            check_typescript
            check_api_keys
            check_common_tools
            ;;
        all)
            check_python
            check_typescript
            check_api_keys
            check_common_tools
            ;;
        *)
            echo "Usage: $0 [python|typescript|all]"
            echo "  python     - Check Python environment only"
            echo "  typescript - Check TypeScript/Node.js environment only"
            echo "  all        - Check both environments (default)"
            exit 1
            ;;
    esac

    print_summary
}

main "$@"
