#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}     DCMS - Contest Management System${NC}"
echo -e "${BLUE}        v2.0 (Client-Side Execution)${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python3 not found! Please install Python 3.8+${NC}"
    exit 1
fi

# Check/Install dependencies
echo "[1/4] Checking dependencies..."
pip3 show fastapi &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install fastapi uvicorn websockets requests -q
fi

# Setup database
echo "[2/4] Setting up database..."
if [ ! -f dcms.db ]; then
    python3 db_setup.py
else
    echo "Database already exists."
fi

# Start server
echo "[3/4] Starting server..."
python3 main.py &
SERVER_PID=$!

# Wait for server
echo "[4/4] Waiting for server to start..."
sleep 3

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN} Server running at http://127.0.0.1:8000${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""

show_menu() {
    echo "Choose an option:"
    echo "  1. Open Admin Dashboard"
    echo "  2. Open Client (Participant)"
    echo "  3. Open Both"
    echo "  4. Stop Server & Exit"
    echo ""
}

while true; do
    show_menu
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1)
            echo "Starting Admin Dashboard..."
            python3 admin_gui.py &
            echo "Admin Dashboard started!"
            ;;
        2)
            echo "Starting Client..."
            python3 client_gui.py &
            echo "Client started!"
            ;;
        3)
            echo "Starting Admin Dashboard..."
            python3 admin_gui.py &
            sleep 1
            echo "Starting Client..."
            python3 client_gui.py &
            echo "Both applications started!"
            ;;
        4)
            echo "Stopping server..."
            kill $SERVER_PID 2>/dev/null
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice!${NC}"
            ;;
    esac
    echo ""
done