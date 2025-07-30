# FPL Squad Optimizer ⚽

A comprehensive Fantasy Premier League assistant that uses **machine learning predictions** and **mathematical optimization** to help you build the perfect squad.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

- **Real-time Data Fetching**: Retrieves live player data from the official FPL API
- **Machine Learning Predictions**: XGBoost model predicts player points for upcoming gameweeks  
- **Advanced Squad Optimization**: Linear programming finds optimal 15-player squads within budget
- **Fixture Difficulty Rating (FDR)**: Analyzes opponent strength for better player selection
- **Interactive Web Interface**: Beautiful Streamlit app with optimization controls and statistics
- **Next 3 Gameweeks Analysis**: Comprehensive fixture analysis with position-specific recommendations
- **Manual Player Selection**: Force include/exclude specific players
- **Team Position Limits**: Prevents over-concentration from single teams
- **Expensive Player Strategy**: Smart handling of premium players (Salah, Haaland, etc.)
- **Advanced Filtering**: Team exclusions, FDR settings, budget controls

## 🏗️ Project Structure

```
FPL-Squad-Optimizer/
├── data/
│   ├── raw/                    # Raw JSON data from FPL API
│   │   ├── fpl_data_latest.json
│   │   └── fpl_fixtures_latest.json
│   └── processed/              # Cleaned CSV data
│       └── fpl_players_latest.csv
├── src/
│   ├── fetch_fpl_data.py      # Data fetching with FDR calculations
│   └── optimizer.py           # Squad optimization engine
├── models/                     # Trained ML models (*.pkl files)
├── notebooks/                  # Jupyter notebooks for analysis
│   └── model_training.ipynb   # Model training and evaluation
├── web_app/
│   ├── app.py                 # Main Streamlit web application
│   └── assets/                # Images and documentation
├── tests/                     # Test files
│   └── test_app.py           # Application tests
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── run.sh                     # Quick start script
└── README.md                  # Project documentation
```

## 🚀 Quick Start

**One-command setup:**
```bash
./run.sh
```

Or follow manual setup below:

## 🛠️ Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/FPL-Squad-Optimizer.git
   cd FPL-Squad-Optimizer
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Fetch FPL data:**
   ```bash
   python3 src/fetch_fpl_data.py
   ```

5. **Train the model (optional):**
   ```bash
   jupyter notebook notebooks/model_training.ipynb
   # Run all cells to train and save the model
   ```

6. **Run the web app:**
   ```bash
   streamlit run web_app/app.py
   # Opens at http://localhost:8501
   ```

## 🎯 Usage

### Data Fetching
The `fetch_fpl_data.py` script downloads player data from the FPL API and processes it for modeling:
- **804 players** with **43+ features** including FDR calculations
- **Team strength data** for fixture difficulty analysis
- **Real-time updates** from official FPL API

### Machine Learning
The Jupyter notebook trains models to predict player points based on:
- Current form and historical performance
- Playing time (minutes) and cost efficiency
- **XGBoost**, **Random Forest**, and **Linear Regression** models

### Squad Optimization
The optimizer uses **linear programming** (PuLP) to select optimal squads considering:
- **Budget constraints** (default: £100.0m)
- **Position requirements** (2 GK, 5 DEF, 5 MID, 3 FWD)
- **Maximum 3 players per team**
- **FDR integration** for fixture difficulty
- **Team-specific position limits**
- **Expensive player strategy** (prioritizes premium players in starting XI)

### Web Interface
The Streamlit app provides:
- **Squad Optimizer**: Interactive controls for budget, FDR settings, team limits
- **Player Statistics**: Comprehensive stats with top 10 leaderboards
- **Beautiful visualizations**: Charts and tables with professional styling

## 🔧 Key Features Explained

### Fixture Difficulty Rating (FDR)
- **Attack FDR**: How difficult it is for players to score/assist against upcoming opponents
- **Defence FDR**: How difficult it is for defenders/goalkeepers to keep clean sheets
- **Overall FDR**: Combined difficulty rating for balanced player evaluation

### Team Position Limits
Prevents algorithm from selecting too many players from the same position in one team:
- Max 2 defenders from any single team
- Max 2 midfielders from any single team  
- Max 1 forward from any single team
- Max 1 goalkeeper from any single team

### Expensive Player Strategy
Smart handling of premium players (£8.0m+):
- **Starting XI Priority**: Expensive players get 2.0x bonus for starting positions
- **Bench Limitations**: Maximum 1 very expensive player (£10.0m+) allowed on bench
- **Cost Integration**: Higher cost players weighted toward starting XI

## 📈 Model Performance

The machine learning models achieve:
- **XGBoost**: Best overall performance for point predictions
- **Feature Importance**: Form, minutes, cost efficiency, historical data
- **Cross-validation**: Robust training with multiple validation folds

## 🎮 API Usage

This project uses the official Fantasy Premier League API:
- **Endpoint**: `https://fantasy.premierleague.com/api/bootstrap-static/`
- **No authentication required**
- **Rate limiting respected**
- **Real-time data updates**

## 📊 Sample Output

### Optimal Squad Example:
```
Starting XI (£98.5m):
GK: Alisson (£5.5m) - Liverpool
DEF: Alexander-Arnold (£7.1m) - Liverpool  
DEF: Saliba (£5.9m) - Arsenal
DEF: Trippier (£6.2m) - Newcastle
MID: Salah (£13.6m) - Liverpool
MID: De Bruyne (£12.1m) - Man City
MID: Saka (£11.2m) - Arsenal
MID: Palmer (£10.7m) - Chelsea
FWD: Haaland (£14.9m) - Man City
FWD: Watkins (£9.1m) - Aston Villa
FWD: Isak (£8.4m) - Newcastle

Bench:
GK: Flekken (£4.6m) - Brentford
DEF: Konsa (£4.8m) - Aston Villa
MID: Luis Díaz (£7.9m) - Liverpool
FWD: Wood (£6.2m) - Newcastle
```

## ⚠️ Disclaimer

**Educational Purpose Only**: This tool is created for educational and research purposes. It should not encourage gambling or financial risk-taking.

**No Guarantees**: Player performance predictions are estimates based on historical data and statistical models. Actual results may vary significantly.

**Use Responsibly**: Fantasy football should be played for entertainment. Please play responsibly and within your means.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fantasy Premier League API** for providing comprehensive player data
- **Streamlit** for the amazing web app framework
- **Plotly** for beautiful interactive visualizations
- **scikit-learn & XGBoost** for machine learning capabilities
- **PuLP** for linear programming optimization

---

**⭐ If you find this project helpful, please give it a star!**

**🔗 Connect with me:** [GitHub](https://github.com/YOUR_USERNAME) | [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)

## Quick Start

🚀 **One-command setup:**
```bash
./run.sh
```

Or follow manual setup below:

## Manual Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Fetch FPL data:**
   ```bash
   python3 src/fetch_fpl_data.py
   ```

4. **Train the model (optional):**
   ```bash
   jupyter notebook notebooks/model_training.ipynb
   # Run all cells to train and save the model
   ```

5. **Run the web app:**
   ```bash
   streamlit run web_app/app.py
   # Opens at http://localhost:8501
   ```

## Quick Commands

- **Fetch latest data:** `python3 src/fetch_fpl_data.py`
- **Run optimizer CLI:** `python3 src/optimizer.py`
- **Launch web app:** `streamlit run web_app/app.py`
- **Train model:** Open `notebooks/model_training.ipynb` in Jupyter

## Usage

### Data Fetching
The `fetch_fpl_data.py` script downloads player data from the FPL API and processes it for modeling.

### Model Training
The Jupyter notebook trains an XGBoost model to predict player points based on:
- Current form
- Playing time (minutes)
- Cost efficiency
- Historical performance

### Squad Optimization
The optimizer uses linear programming to select the best 15-player squad considering:
- Budget constraints (default: £100.0m)
- Position requirements (2 GK, 5 DEF, 5 MID, 3 FWD)
- Maximum 3 players per team

### Web Interface
The Streamlit app provides an intuitive interface to:
- Adjust budget constraints
- View optimal squad recommendations
- See predicted points and costs

## API Usage

This project uses the official Fantasy Premier League API:
- Endpoint: `https://fantasy.premierleague.com/api/bootstrap-static/`
- No authentication required
- Rate limiting respected

## Sample Output

**Data Fetching:**
```
✅ Loaded 804 players
Positions: {'Midfielder': 347, 'Defender': 268, 'Forward': 87, 'Goalkeeper': 82}
Average cost: £4.7m
Top scorer: Mohamed Salah (344 pts)
```

**Squad Optimization:**
```
🏆 OPTIMAL FPL SQUAD (£100.0m budget)
Total Cost: £80.7m | Remaining: £19.3m | Predicted Points: 154.2

GOALKEEPERS (2): Jordan Pickford, David Raya Martin
DEFENDERS (5): Marc Cucurella, Levi Colwill, Vitalii Mykolenko...
MIDFIELDERS (5): Jack Hinshelwood, Jarrod Bowen, Ilkay Gündogan...
FORWARDS (3): Iliman Ndiaye, Jørgen Strand Larsen, Eddie Nketiah...
```

**Web Interface Features:**
- 📊 Interactive budget slider (£80-120m)
- 🎯 Position-specific weight adjustments
- 📈 Real-time optimization with constraints
- 📋 Downloadable squad lists (CSV)
- 📊 Visual analytics (charts & breakdowns)
- 🔄 Team & position filtering options

## Disclaimer

This project is for educational and portfolio purposes only. It uses publicly available FPL API data and does not include any copyrighted content or logos.

## License

This project is open source and available under the MIT License.
