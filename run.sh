#!/bin/bash

# FPL Project Setup and Run Script

echo "🏆 Fantasy Premier League Squad Optimizer"
echo "=========================================="

# Function to check if command exists

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}


# Check Python installation (use 'python' for Git Bash)
if ! command_exists python; then
    echo "❌ Python is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/Scripts/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if data exists or is outdated
if [ ! -f "data/processed/fpl_players_latest.csv" ] || [ ! -f "data/raw/fpl_data_latest.json" ]; then
    echo "📊 Fetching latest FPL data..."
    python src/fetch_fpl_data.py
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
        python src/fetch_fpl_data.py
        ;;
    2)
        echo "🧠 Opening Jupyter notebook for model training..."
        jupyter notebook notebooks/model_training.ipynb
        ;;
    3)
        echo "⚙️ Running squad optimizer..."
        python src/optimizer.py
        ;;
    4)
        echo "🌐 Launching web application..."
        echo "📱 Opening in browser: http://localhost:8501"
        streamlit run web_app/app.py
        ;;
    5)
        echo "📝 Quick Demo:"
        echo "==============="
        echo "1. Fetching sample data..."
        python src/fetch_fpl_data.py
        echo ""
        echo "2. Running optimizer with £100m budget..."
        python src/optimizer.py
        echo ""
        echo "3. Demo complete! Run option 4 to see the web interface."
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
