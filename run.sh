#!/bin/bash

# FPL Project Setup and Run Script

echo "🏆 Fantasy Premier League Squad Optimizer"
echo "=========================================="

# Function to check if command exists

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Set Python executable path
PYTHON_EXE="D:/FPL_Project/F_PL-Project/.venv/Scripts/python.exe"

# Check Python installation
if [ ! -f "$PYTHON_EXE" ]; then
    echo "❌ Python virtual environment not found at $PYTHON_EXE"
    echo "Please ensure the virtual environment is set up correctly."
    exit 1
fi

# Check if virtual environment exists (.venv directory)
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment (.venv) not found."
    echo "Please set up the virtual environment first."
    exit 1
fi

# Virtual environment is already activated through the Python path
echo "✅ Using virtual environment at .venv"

# Install/update dependencies
echo "📦 Installing dependencies..."
"$PYTHON_EXE" -m pip install -q --upgrade pip
"$PYTHON_EXE" -m pip install -q -r requirements.txt

# Check if data exists or is outdated
if [ ! -f "data/processed/fpl_players_latest.csv" ] || [ ! -f "data/raw/fpl_data_latest.json" ]; then
    echo "📊 Fetching latest FPL data..."
    "$PYTHON_EXE" src/fetch_fpl_data.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to fetch data"
        exit 1
    fi
else
    echo "✅ FPL data found"
fi

echo ""
echo "Choose an option:"
echo "1. 📊 Fetch fresh data"
echo "2. 🧠 Train ML model (Jupyter)"
echo "3. ⚙️  Run optimizer (CLI)"
echo "4. 🌐 Launch web app"
echo "5. 📝 Show quick demo"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "📊 Fetching fresh FPL data..."
        "$PYTHON_EXE" src/fetch_fpl_data.py
        ;;
    2)
        echo "🧠 Opening Jupyter notebook for model training..."
        "$PYTHON_EXE" -m jupyter notebook notebooks/model_training.ipynb
        ;;
    3)
        echo "⚙️ Running squad optimizer..."
        "$PYTHON_EXE" src/optimizer.py
        ;;
    4)
        echo "🌐 Launching web application..."
        echo "📱 Opening in browser: http://localhost:8501"
        "$PYTHON_EXE" -m streamlit run web_app/app.py
        ;;
    5)
        echo "📝 Quick Demo:"
        echo "==============="
        echo "1. Fetching sample data..."
        "$PYTHON_EXE" src/fetch_fpl_data.py
        echo ""
        echo "2. Running optimizer with £100m budget..."
        "$PYTHON_EXE" src/optimizer.py
        echo ""
        echo "3. Demo complete! Run option 4 to see the web interface."
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
