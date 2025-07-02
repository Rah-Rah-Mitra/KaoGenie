#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Helper Function to Check for Command Existence (for non-Windows specific commands) ---
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✔ $2 found.${NC}"
    else
        echo -e "${RED}✖ Error: $2 is not installed or not in your PATH.${NC}"
        echo -e "${YELLOW}Please install $2 and try again.${NC}"
        exit 1
    fi
}

# --- Main Logic ---
echo -e "${YELLOW}Starting AI Exam Generator Setup...${NC}"
echo "This script will check for dependencies and set up the backend and frontend."
echo "-----------------------------------------------------"

# 1. Check for system dependencies
echo "1. Checking for required system dependencies..."
check_command "python3" "Python 3"
check_command "npm" "npm (Node.js package manager)"

# More robust check for 'uv' to handle Windows .exe from bash
echo -n "-> Checking for 'uv' package manager... "
if command -v uv &> /dev/null; then
    UV_CMD="uv"
    echo -e "${GREEN}✔ 'uv' command found.${NC}"
elif command -v uv.exe &> /dev/null; then
    UV_CMD="uv.exe"
    echo -e "${GREEN}✔ 'uv.exe' command found (Windows environment).${NC}"
else
    echo -e "${RED}✖ Error: 'uv' is not installed or not in your PATH.${NC}"
    echo -e "${YELLOW}Please install uv from https://github.com/astral-sh/uv and try again.${NC}"
    exit 1
fi

# More robust check for 'tesseract' to handle Windows .exe from bash
echo -n "-> Checking for 'Tesseract OCR'... "
if command -v tesseract &> /dev/null; then
    echo -e "${GREEN}✔ 'tesseract' command found.${NC}"
elif command -v tesseract.exe &> /dev/null; then
    echo -e "${GREEN}✔ 'tesseract.exe' command found (Windows environment).${NC}"
else
    echo -e "${RED}✖ Error: 'Tesseract OCR' is not installed or not in your PATH.${NC}"
    echo -e "${YELLOW}Please install Tesseract and ensure it's in your system's PATH. See the README for links.${NC}"
    exit 1
fi
echo "-----------------------------------------------------"

# 2. Setup Backend
echo "2. Setting up the Backend..."
cd backend

# Check for and create .env file
if [ -f ".env" ]; then
    echo -e "${YELLOW}ℹ .env file already exists. Skipping creation.${NC}"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✔ .env file created from .env.example.${NC}"
    else
        echo -e "${RED}✖ Error: .env.example not found. Cannot create .env file.${NC}"
        exit 1
    fi
fi

# Verify required keys in .env file
echo "-> Verifying required keys in backend/.env file..."
REQUIRED_KEYS=("OPENAI_API_KEY" "GOOGLE_API_KEY" "GOOGLE_CSE_ID")
all_keys_present=true
for key in "${REQUIRED_KEYS[@]}"; do
    if ! grep -q -E "^${key}=.+[^\"']" .env; then
        echo -e "${RED}✖ Warning: Key '${key}' is missing or has no value in the backend/.env file.${NC}"
        all_keys_present=false
    fi
done

if [ "$all_keys_present" = false ]; then
    echo -e "${YELLOW}Please ensure all required keys in 'backend/.env' are set to valid values.${NC}"
else
    echo -e "${GREEN}✔ All required keys are present in the .env file.${NC}"
fi

# Install Python dependencies using the detected uv command
echo "-> Creating Python virtual environment with '$UV_CMD'..."
$UV_CMD venv > /dev/null 2>&1
echo "-> Installing Python dependencies with '$UV_CMD' (this may take a few minutes)..."
$UV_CMD pip install -r requirements.txt
echo -e "${GREEN}✔ Backend dependencies installed successfully.${NC}"
cd ..
echo "-----------------------------------------------------"

# 3. Setup Frontend
echo "3. Setting up the Frontend..."
cd frontend
echo "-> Installing npm dependencies (this may take a few minutes)..."
npm install
echo -e "${GREEN}✔ Frontend dependencies installed successfully.${NC}"
cd ..
echo "-----------------------------------------------------"

echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo -e "Next steps:"
echo -e "1. (If you haven't already) Open 'backend/.env' and fill in your secret API keys."
echo -e "2. Start the backend server (in one terminal):"
echo -e "   ${YELLOW}cd backend${NC}"
echo -e "   ${YELLOW}# On macOS/Linux/Git Bash/WSL:${NC}"
echo -e "   ${YELLOW}source .venv/bin/activate${NC}"
echo -e "   ${YELLOW}# On Windows (CMD/PowerShell):${NC}"
echo -e "   ${YELLOW}.venv\\Scripts\\activate${NC}"
echo -e "   ${YELLOW}uvicorn main:app --host 0.0.0.0 --port 1234 --reload${NC}"
echo ""
echo -e "3. Start the frontend server (in another terminal):"
echo -e "   ${YELLOW}cd frontend && npm run dev${NC}"
echo ""