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
echo "2. 🧠 Train advanced ML models"
echo "3. ⚙️  Run optimizer (CLI)"
echo "4. 🌐 Launch web app (with ML models)"
echo "5. 📝 Show quick demo"
echo "6. 🤖 Verify ML models status"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "📊 Fetching fresh FPL data..."
        "$PYTHON_EXE" src/fetch_fpl_data.py
        ;;
    2)
        echo "🧠 Training advanced ML models (Markov Chain + Age Analysis + News Sentiment)..."
        echo "This will create sophisticated prediction models for better recommendations."
        "$PYTHON_EXE" src/train_advanced_models.py
        if [ $? -eq 0 ]; then
            echo "✅ Advanced ML models trained successfully!"
        else
            echo "❌ Model training failed. Check the logs above."
        fi
        ;;
    3)
        echo "⚙️ Running squad optimizer..."
        "$PYTHON_EXE" src/optimizer.py
        ;;
    4)
        echo "🤖 Checking ML models before launching web app..."
        
        # Check if advanced models exist
        if [ -f "models/ensemble_random_forest.pkl" ] && [ -f "models/markov_model.pkl" ]; then
            echo "✅ Advanced ML models found"
        else
            echo "⚠️  Advanced ML models not found. Training them now..."
            "$PYTHON_EXE" src/train_advanced_models.py
            if [ $? -ne 0 ]; then
                echo "❌ Model training failed. Launching with basic models..."
            fi
        fi
        
        echo "🌐 Launching web application with advanced ML predictions..."
        echo "📱 Opening in browser: http://localhost:8501"
        echo "🤖 Features: Markov Chain + Age Analysis + News Sentiment + Fixture Intelligence"
        "$PYTHON_EXE" -m streamlit run web_app/app.py
        ;;
    5)
        echo "📝 Quick Demo with Advanced ML:"
        echo "==============================="
        echo "1. Fetching sample data..."
        "$PYTHON_EXE" src/fetch_fpl_data.py
        echo ""
        echo "2. Training advanced ML models..."
        "$PYTHON_EXE" src/train_advanced_models.py
        echo ""
        echo "3. Running optimizer with £100m budget and advanced predictions..."
        "$PYTHON_EXE" src/optimizer.py
        echo ""
        echo "4. Demo complete! Run option 4 to see the web interface with ML predictions."
        ;;
    6)
        echo "🤖 Checking ML Models Status:"
        echo "============================="
        
        # Check model files
        echo "📁 Checking model files..."
        if [ -d "models" ]; then
            echo "✅ Models directory exists"
            ls -la models/
        else
            echo "❌ Models directory not found"
        fi
        
        # Test model loading
        echo ""
        echo "🧪 Testing model loading..."
        "$PYTHON_EXE" -c "
import sys
sys.path.append('src')
try:
    from advanced_ml_models import EnsemblePredictor
    print('✅ Advanced ML models imported successfully')
    
    ensemble = EnsemblePredictor()
    ensemble.load_models()
    print('✅ All advanced ML models loaded successfully')
    print('🤖 Available: Markov Chain + Age Analysis + News Sentiment + Ensemble')
except Exception as e:
    print(f'❌ Error loading models: {e}')
    print('💡 Run option 2 to train the models')
"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
