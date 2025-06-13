#!/bin/bash

# FPL Project Setup and Run Script

echo "🏆 Fantasy Premier League Squad Optimizer"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if data exists
if [ ! -f "data/processed/fpl_players_latest.csv" ]; then
    echo "📊 Fetching latest FPL data..."
    python3 src/fetch_fpl_data.py
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
        python3 src/fetch_fpl_data.py
        ;;
    2)
        echo "🧠 Opening Jupyter notebook for model training..."
        jupyter notebook notebooks/model_training.ipynb
        ;;
    3)
        echo "⚙️ Running squad optimizer..."
        python3 src/optimizer.py
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
        python3 src/fetch_fpl_data.py
        echo ""
        echo "2. Running optimizer with £100m budget..."
        python3 src/optimizer.py
        echo ""
        echo "3. Demo complete! Run option 4 to see the web interface."
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
