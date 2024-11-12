#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display error and exit
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Check for required commands
echo "Checking prerequisites..."
command_exists gh || error_exit "GitHub CLI (gh) is not installed. Please install it first."
command_exists npm || error_exit "npm is not installed. Please install Node.js and npm first."
command_exists git || error_exit "git is not installed. Please install it first."

# Check if user is authenticated with GitHub CLI
if ! gh auth status >/dev/null 2>&1; then
    error_exit "Please login to GitHub CLI first using 'gh auth login'"
fi

# Check if package.json exists
[ -f package.json ] || error_exit "package.json not found. Are you in the correct directory?"

# Check if git repository exists
[ -d .git ] || error_exit "Git repository not found. Please initialize one first."

# Install gh-pages if not already installed
echo -e "${YELLOW}Installing/updating gh-pages package...${NC}"
npm install --save-dev gh-pages

# Get repository information
REPO_NAME=$(gh repo view --json name -q .name)
REPO_OWNER=$(gh repo view --json owner -q .owner.login)

# Update next.config.js
echo -e "${YELLOW}Updating next.config.js...${NC}"
cat > next.config.js << EOL
/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    basePath: '/${REPO_NAME}',
    images: {
        unoptimized: true,
    },
}

module.exports = nextConfig
EOL

# Check if homepage is set in package.json
if ! grep -q '"homepage":' package.json; then
    echo -e "${YELLOW}Adding homepage field to package.json...${NC}"
    if command_exists jq; then
        jq --arg url "https://${REPO_OWNER}.github.io/${REPO_NAME}" \
           '. + {homepage: $url}' package.json > package.json.tmp && mv package.json.tmp package.json
    else
        sed -i.bak 's/"name": \(".*"\)/&,\n  "homepage": "https:\/\/'"${REPO_OWNER}"'.github.io\/'"${REPO_NAME}"'"/' package.json
        rm package.json.bak
    fi
fi

# Update deploy scripts in package.json
echo -e "${YELLOW}Updating deploy scripts in package.json...${NC}"
if command_exists jq; then
    jq '.scripts += {
        "predeploy": "npm run build",
        "deploy": "touch out/.nojekyll && gh-pages -d out --dotfiles"
    }' package.json > package.json.tmp && mv package.json.tmp package.json
else
    sed -i.bak 's/"scripts": {/"scripts": {\n    "predeploy": "npm run build",\n    "deploy": "touch out\/.nojekyll \&\& gh-pages -d out --dotfiles",/' package.json
    rm package.json.bak
fi

# Build and deploy
echo -e "${YELLOW}Building and deploying your Next.js app...${NC}"
npm run deploy

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Deployment successful!${NC}"
    
    # Get the homepage URL from package.json
    HOMEPAGE_URL=$(grep -o '"homepage": *"[^"]*"' package.json | cut -d'"' -f4)
    echo -e "${GREEN}Your app should be available at: ${HOMEPAGE_URL}${NC}"
    
    # Configure GitHub Pages in repository settings using GitHub CLI
    echo "Configuring GitHub Pages settings..."
    gh api -X PUT /repos/${REPO_OWNER}/${REPO_NAME}/pages \
        -f source='{"branch":"gh-pages","path":"/"}' >/dev/null 2>&1
    
    echo -e "${YELLOW}Note: It might take a few minutes for the changes to be reflected on GitHub Pages.${NC}"
else
    error_exit "Deployment failed"
fi