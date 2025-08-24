# FPL Squad Optimizer ⚽

A comprehensi### 🏆 Curren### 📅 Next 3 Gameweeks Fixture Analysis
- **Position-Specific FDR**: Attack and defense difficulty ratings tailored by player position
- **Strategic Recommendations**: Captaincy suggestions and transfer priority rankings
- **Team Form Integration**: Recent performance trends combined with fixture difficulty
- **Fixture Congestion Analysis**: Multiple games per week identification and impact assessment
- **Opposition Analysis**: Detailed breakdown of upcoming opponents' defensive/attacking strengthson Points Analysis
- **Live Gameweek Tracking**: Real-time current and previous gameweek performance monitoring
- **Season Leaderboards**: Comprehensive rankings across all major statistical categories
- **Form Analysis**: Hot/cold form identification with 5-game rolling averages
- **Value Discovery**: Budget options under £6m, differential picks under 5% ownership
- **Transfer Intelligence**: Most transferred in/out players with ownership percentage analysis
- **Performance Trends**: Visual charts showing player trajectory and consistency patternstasy Premier League assistant that uses **machine learning predictions** and **mathematical optimization** to help you build the perfect squad.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)

## 🚀 Features

### 🎯 Advanced Squad Optimization
- **Strategic Weight System**: 7-factor prediction model balancing recent momentum with strategic planning
  - **Fixture Advantage**: 25% (Primary focus on upcoming opponent difficulty)
  - **Last 5 Matches**: 20% (Recent momentum and current form)
  - **Season Performance**: 20% (Overall consistency and reliability)
  - **PPG Consistency**: 15% (Points per game sustainability)
  - **Value Factor**: 10% (Points per million efficiency)
  - **Form (10 games)**: 5% (Extended form context)
  - **Top 5 Team Bonus**: 5% (Big team player reliability boost)
- **Mathematical Optimization**: Uses PuLP linear programming for optimal 15-player squads
- **Smart Constraints**: Budget (£80-120m), formation requirements, team diversity (max 3 per team)
- **Manual Controls**: Force include/exclude specific players
- **Multi-Method Predictions**: Ensemble ML models with strategic weight fallback

### 🧠 Advanced ML Prediction System
- **Ensemble Models**: Random Forest + Gradient Boosting + Markov Chain integration
- **Markov Chain Form Predictor**: Analyzes historical form transition patterns for sustainability
- **Age & Injury Analysis**: Position-specific performance curves and injury impact modeling
- **News Sentiment Integration**: Real-time analysis of transfer rumors and injury updates
- **Feature Engineering**: 40+ statistical features with advanced interaction detection
- **Robust Fallback**: Strategic weights ensure reliability when ML models unavailable

### 📊 Comprehensive Player Statistics
- **25+ Statistical Categories**: Goals, assists, clean sheets, bonus points, ICT index, minutes, and more
- **6 Analysis Tabs**: Top Performers, Attack Stats, Defense Stats, General Stats, Advanced Stats, Team Analysis
- **Professional Data Tables**: Left-aligned formatting with consistent styling and search functionality
- **Interactive Filtering**: Search by player name, team, or position across all statistics
- **Value Analysis**: Best value players, differential picks, budget gems, and ownership trends

### � Current Season Points Analysis
- **Live Gameweek Data**: Real-time current and previous gameweek performance tracking
- **Season Leaders**: Comprehensive leaderboards across all major statistical categories
- **Form Analysis**: Player performance trends and hot/cold form identification
- **Value Discovery**: Budget options, differential picks, and best value players
- **Transfer Trends**: Most transferred in/out players with ownership analysis

### �🔮 Next 3 Gameweeks Analysis
- **Fixture Difficulty Rating (FDR)**: Analyzes opponent strength for better player selection
- **Position-Specific Recommendations**: Tailored advice for GK, DEF, MID, FWD
- **Team Performance Metrics**: Form analysis and upcoming fixture difficulty
- **Strategic Insights**: Captain picks and transfer recommendations

### 🌐 Professional Web Interface
- **Modern Streamlit Design**: Responsive layout with FPL theme colors (#37003c, #00ff87)
- **Real-time Data Pipeline**: Live FPL API integration with intelligent 5-minute caching
- **4-Page Navigation**: Squad Optimizer, Player Statistics, Next 3 Gameweeks, Current Season Points
- **Interactive Visualizations**: Plotly charts, performance graphs, and dynamic tables
- **Data Quality Assurance**: Automatic validation, error handling, and graceful fallbacks
- **Session Management**: Persistent user preferences and cross-page state retention

## 🏗️ Project Structure

```
F_PL-Project/
├── .venv/                           # Virtual environment (auto-created)
├── data/
│   ├── raw/                          # Raw JSON data from FPL API
│   │   ├── fpl_data_latest.json     # Player data and statistics
│   │   └── fpl_fixtures_latest.json # Fixture and team data
│   └── processed/                    # Cleaned CSV data ready for analysis
│       └── fpl_players_latest.csv   # Processed player data with FDR
├── models/                          # Trained ML models (auto-generated)
│   ├── ensemble_random_forest.pkl   # Random Forest ensemble model
│   ├── ensemble_gradient_boost.pkl  # Gradient Boosting model
│   ├── markov_model.pkl             # Markov Chain form predictor
│   ├── ensemble_weights.pkl         # Model combination weights
│   └── scaler.pkl                   # Feature scaling parameters
├── src/
│   ├── fetch_fpl_data.py            # Data fetching with FDR calculations
│   ├── optimizer.py                 # Squad optimization engine with ML integration
│   ├── advanced_ml_models.py        # ML model implementations (Markov, ensemble, sentiment)
│   └── train_advanced_models.py     # Model training and validation pipeline
├── web_app/
│   ├── app.py                       # Main Streamlit application entry point
│   ├── FPL_Squad_Optimizer.py      # Squad optimization page with strategic weights
│   ├── FPL_Player_Statistics.py    # Comprehensive player statistics and analysis
│   ├── Next_3_Gameweeks.py         # Fixture analysis with position-specific FDR
│   ├── Current_Season_Points.py    # Live gameweek tracking and season analysis
│   ├── performance_utils.py         # Performance analysis utilities
│   └── utils.py                     # Shared utilities and navigation functions
├── .gitignore                       # Git ignore rules
├── requirements.txt                 # Production dependencies
├── run.sh                          # Interactive setup and launch script (Windows compatible)
├── pyproject.toml                  # Modern Python project configuration
├── LICENSE                         # MIT license
└── README.md                       # This documentation
```

## 🚀 Quick Start

**One-command interactive setup:**
```bash
./run.sh
```

The enhanced script will guide you through:
1. 📊 Fetch fresh FPL data
2. ⚙️ Run optimizer (CLI)
3. 🌐 Launch web app
4. 📝 Show quick demo

**Note**: The script automatically detects and uses the correct Python executable path for Windows compatibility, including full virtual environment support.

**Alternative direct commands:**
```bash
# For Git Bash on Windows
bash run.sh

# Direct web app launch
streamlit run web_app/app.py
```

## 🛠️ Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ataullahkhanrifat/F_PL-Project.git
   cd F_PL-Project
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # On Windows Git Bash
   # source .venv/bin/activate    # On Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Fetch FPL data:**
   ```bash
   python src/fetch_fpl_data.py
   ```

5. **Run the web app:**
   ```bash
   streamlit run web_app/app.py
   # Opens at http://localhost:8501
   ```

## 🎯 Usage Guide

### 📊 Data Management
- **Automatic Fetching**: Real-time player data from official FPL API
- **800+ Players**: Complete dataset with 40+ features per player
- **FDR Integration**: Fixture Difficulty Rating calculations
- **Clean Processing**: Filtered data ready for optimization

### 🔧 Squad Optimization
The optimizer considers multiple constraints:
- **Budget**: £80-120m range (default £100m)
- **Formation**: 2 GK, 5 DEF, 5 MID, 3 FWD
- **Team Limits**: Maximum 3 players per Premier League team
- **Manual Picks**: Include/exclude specific players
- **Value Focus**: Maximize points per million spent

### 📈 Player Statistics
Comprehensive analysis across 6 main categories:
- **Top Performers**: Highest points, form, ICT index, minutes
- **Attack Stats**: Goals, assists, involvement, efficiency
- **Defense Stats**: Clean sheets, saves, penalties, own goals
- **General Stats**: Cards, bonus points, ownership, BPS
- **Advanced Stats**: Influence, creativity, threat, transfers
- **Team Analysis**: Performance by club with visualizations

### � Current Season Analysis
Live tracking and analysis across 5 comprehensive tabs:
- **Current GW**: Top performers in the active gameweek with live scoring
- **Previous GW**: Form analysis and high-performing players from recent games
- **Season Leaders**: Overall leaderboards for points, goals, assists, and value
- **Form Analysis**: Hot/cold form categories with transfer trends
- **Value Players**: Budget options, differentials, and ownership analysis

### �🔮 Fixture Analysis
Strategic insights for upcoming gameweeks:
- **FDR Ratings**: Attack and defense difficulty by position
- **Team Form**: Recent performance trends
- **Fixture Congestion**: Multiple games per week analysis
- **Captain Recommendations**: Best picks for (C) and (VC)

## 🔧 Key Features Explained

### 🎯 Squad Optimization Engine
- **Linear Programming**: Uses PuLP library for mathematical optimization
- **Multi-Constraint Solving**: Handles budget, position, and team constraints simultaneously
- **Real-time Calculations**: Instant results as you adjust parameters
- **Smart Defaults**: Pre-configured with sensible FPL constraints

### 📊 Advanced Statistics Dashboard
- **Left-Aligned Tables**: Professional data presentation with consistent formatting
- **Interactive Filtering**: Search and filter across all player data
- **Performance Metrics**: 25+ statistical categories with top 10 leaderboards
- **Team Analysis**: Aggregate statistics by Premier League club
- **Visual Charts**: Bar charts and performance graphs

### 🔮 Fixture Difficulty System
- **Attack FDR**: How difficult it is for players to score/assist against upcoming opponents
- **Defense FDR**: How difficult it is for defenders/goalkeepers to keep clean sheets
- **Position-Specific**: Different FDR calculations for each position type
- **3-Gameweek Outlook**: Strategic planning for upcoming fixtures

### 🌐 Web Application Features
- **4-Page Navigation**: Squad Optimizer, Player Statistics, Next 3 Gameweeks, Current Season Points
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Custom Styling**: Professional appearance with branded colors and fonts
- **Real-time Data**: Live FPL API integration with intelligent caching
- **Data Validation**: Automatic checks for data quality and availability
- **Error Handling**: Graceful fallbacks when data is unavailable

## 📈 Technical Implementation

### Modern Python Project Structure
- **pyproject.toml**: Modern Python project configuration following PEP 518/621 standards
- **Virtual Environment**: Uses `.venv` directory for better IDE integration
- **Cross-Platform Compatibility**: Enhanced Windows support with proper path handling
- **Version Management**: Semantic versioning (currently v2.0.0)

### Data Pipeline
- **FPL API Integration**: Direct connection to `https://fantasy.premierleague.com/api/`
- **Data Processing**: Pandas-based cleaning and feature engineering
- **FDR Calculations**: Custom algorithms for fixture difficulty analysis
- **Caching**: Efficient data storage and retrieval

### Strategic Prediction Engine
- **7-Factor Weight System**: Balances fixtures (25%), recent form (20%), season performance (20%), consistency (15%), value (10%), extended form (5%), and big team bonus (5%)
- **Ensemble ML Pipeline**: Random Forest + Gradient Boosting + Markov Chain models with intelligent fallback
- **Feature Engineering**: 40+ statistical features with interaction detection and position-specific analysis
- **Robust Architecture**: Strategic weights ensure reliable predictions when ML models are unavailable

### Advanced ML Models
- **Markov Chain Form Predictor**: Analyzes historical form transitions to predict performance sustainability
- **Random Forest Ensemble**: Discovers complex feature interactions and non-linear patterns
- **Gradient Boosting Corrector**: Sequential error reduction and edge case handling
- **News Sentiment Analysis**: Real-time processing of transfer rumors and injury updates
- **Age/Performance Curves**: Position-specific decline models and injury impact assessment

### Optimization Algorithm
- **Objective Function**: Maximize predicted points within FPL constraints
- **Multi-Constraint Solving**: Budget (£80-120m), formation (2-5-5-3), team diversity (max 3 per team)
- **Linear Programming**: PuLP with CBC optimizer for mathematically optimal solutions
- **Real-time Performance**: Sub-second optimization with manual player inclusion/exclusion

### Web Framework
- **Frontend**: Streamlit with custom CSS using FPL theme colors (#37003c, #00ff87)
- **Backend**: Python with pandas for data manipulation and real-time API integration
- **Visualization**: Plotly for interactive charts and graphs
- **Caching Strategy**: 5-minute TTL for live data with @st.cache_data decorators
- **State Management**: Session-based user preferences and multi-page navigation
- **Error Handling**: Comprehensive validation and graceful error recovery
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## 🎮 API Usage

This project uses the official Fantasy Premier League API:
- **Primary Endpoint**: `https://fantasy.premierleague.com/api/bootstrap-static/`
- **No authentication required** - Public API access
- **Rate limiting respected** - Responsible data fetching with caching
- **Real-time data** - Live player statistics, prices, and gameweek information
- **Comprehensive data** - 800+ players with 40+ features each
- **Live Updates**: Current gameweek scores, transfers, and form data

## 📊 Sample Output

### 🏆 Optimal Squad Example (Strategic Weight System):
```
💰 BUDGET: £100.0m | SPENT: £99.8m | REMAINING: £0.2m
🎯 PREDICTED POINTS: 1,847 (Season Total)
📊 PREDICTION METHOD: Strategic Weights (Fixtures 25% + Last5 20% + Season 20% + PPG 15% + Value 10% + Form10 5% + Top5 5%)

STARTING XI:
GK  Alisson (£5.5m)           - Liverpool     [Prediction: 156 pts]
DEF Alexander-Arnold (£7.1m)   - Liverpool     [Prediction: 178 pts] 
DEF Saliba (£5.9m)            - Arsenal       [Prediction: 145 pts]
DEF Trippier (£6.2m)          - Newcastle     [Prediction: 142 pts]
MID Salah (£13.6m)            - Liverpool     [Prediction: 287 pts]
MID De Bruyne (£12.1m)        - Man City      [Prediction: 245 pts]
MID Saka (£11.2m)             - Arsenal       [Prediction: 232 pts]
MID Palmer (£10.7m)           - Chelsea       [Prediction: 218 pts]
FWD Haaland (£14.9m)          - Man City      [Prediction: 298 pts]
FWD Watkins (£9.1m)           - Aston Villa   [Prediction: 189 pts]
FWD Isak (£8.4m)              - Newcastle     [Prediction: 167 pts]

BENCH:
GK  Flekken (£4.6m)           - Brentford     [Prediction: 125 pts]
DEF Konsa (£4.8m)             - Aston Villa   [Prediction: 98 pts]
MID Luis Díaz (£7.9m)         - Liverpool     [Prediction: 142 pts]
FWD Wood (£6.2m)              - Newcastle     [Prediction: 89 pts]

STRATEGIC INSIGHTS:
🔥 High Fixture Weight (25%): Prioritizes players with favorable upcoming opponents
⚡ Recent Momentum (20%): Emphasizes last 5 matches form for current performance
🏆 Season Reliability (20%): Balances with proven consistent performers
💎 Value Efficiency (10%): Optimizes points per million across the squad
```

### 📈 Player Statistics Sample:
```
🏆 TOP 10 POINTS SCORERS:
1. Mohamed Salah (Liverpool)     - 344 pts, £13.6m
2. Erling Haaland (Man City)     - 338 pts, £14.9m
3. Bukayo Saka (Arsenal)         - 286 pts, £11.2m
4. Cole Palmer (Chelsea)         - 275 pts, £10.7m
5. Ollie Watkins (Aston Villa)   - 256 pts, £9.1m

🎯 TOP 5 ASSIST PROVIDERS:
1. Mohamed Salah (Liverpool)     - 13 assists
2. Cole Palmer (Chelsea)         - 11 assists
3. Bruno Fernandes (Man Utd)     - 10 assists
4. Kevin De Bruyne (Man City)    - 9 assists
5. Bukayo Saka (Arsenal)         - 9 assists
```

### 📊 Current Season Points Sample:
```
🏆 GAMEWEEK 15 ANALYSIS:
Current Status: In Progress | Average Score: 45 pts | Deadline: Dec 15, 2024

🔥 TOP GAMEWEEK PERFORMERS:
1. Mohamed Salah (Liverpool)     - 18 pts (2 goals, 1 assist, 3 bonus)
2. Erling Haaland (Man City)     - 16 pts (2 goals, 2 bonus)
3. Cole Palmer (Chelsea)         - 14 pts (1 goal, 2 assists, 1 bonus)

📈 FORM ANALYSIS (Last 5 Games):
🔥 Hot Form (5.0+ avg): 12 players including Salah (7.2), Haaland (6.8)
📈 Good Form (3.0-4.9): 89 players in consistent scoring form
❄️ Cold Form (0-2.9): 45 players struggling for points

💎 BEST VALUE PLAYERS:
1. Jhon Durán (Aston Villa)      - 15.2 value, £5.2m
2. Morgan Gibbs-White (Forest)   - 12.8 value, £6.1m
3. Chris Wood (Newcastle)        - 11.9 value, £6.2m
```

### 🔮 Fixture Analysis Sample (Position-Specific FDR):
```
📅 NEXT 3 GAMEWEEKS ANALYSIS (Strategic Weight System: Fixtures 25%)

GW15: Liverpool (H) vs Brighton
┌─────────────────┬─────────────┬──────────────────┐
│ Position        │ Attack FDR  │ Defense FDR      │
├─────────────────┼─────────────┼──────────────────┤
│ Forwards        │ 2/5 (Easy)  │ N/A              │
│ Midfielders     │ 2/5 (Easy)  │ N/A              │
│ Defenders       │ N/A         │ 3/5 (Average)    │
│ Goalkeepers     │ N/A         │ 3/5 (Average)    │
└─────────────────┴─────────────┴──────────────────┘
🎯 Strategic Recommendation: Strong captain option for Salah/Núñez
💡 Weight Impact: 25% fixture boost for Liverpool attackers

GW16: Arsenal (A) vs Man City  
┌─────────────────┬─────────────┬──────────────────┐
│ Position        │ Attack FDR  │ Defense FDR      │
├─────────────────┼─────────────┼──────────────────┤
│ Forwards        │ 4/5 (Hard)  │ N/A              │
│ Midfielders     │ 4/5 (Hard)  │ N/A              │
│ Defenders       │ N/A         │ 4/5 (Difficult) │
│ Goalkeepers     │ N/A         │ 4/5 (Difficult) │
└─────────────────┴─────────────┴──────────────────┘
🚫 Strategic Recommendation: Avoid Arsenal attackers, consider City defense
⚠️ Weight Impact: 25% fixture penalty for both teams' attacking returns

GW17: Newcastle (H) vs Brentford
┌─────────────────┬─────────────┬──────────────────┐
│ Position        │ Attack FDR  │ Defense FDR      │
├─────────────────┼─────────────┼──────────────────┤
│ Forwards        │ 2/5 (Easy)  │ N/A              │
│ Midfielders     │ 2/5 (Easy)  │ N/A              │
│ Defenders       │ N/A         │ 2/5 (Easy)       │
│ Goalkeepers     │ N/A         │ 2/5 (Easy)       │
└─────────────────┴─────────────┴──────────────────┘
⭐ Strategic Recommendation: Newcastle double-up opportunity
🏆 Weight Impact: 25% fixture boost for both attacking and defensive Newcastle assets
```

## ⚠️ Disclaimer

**Educational Purpose Only**: This tool is created for educational and research purposes. It should not encourage gambling or financial risk-taking.

**No Guarantees**: Player performance predictions are estimates based on historical data and statistical models. Actual results may vary significantly.

**Use Responsibly**: Fantasy football should be played for entertainment. Please play responsibly and within your means.

**API Usage**: This project uses publicly available FPL API data and respects all rate limiting. No copyrighted content or official FPL logos are included.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
git clone https://github.com/ataullahkhanrifat/F_PL-Project.git
cd F_PL-Project
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
```

### Areas for Contribution
- 🧠 Machine learning model improvements
- 📊 Additional statistical analysis features  
- 🎨 UI/UX enhancements
- 🔧 Performance optimizations
- 📝 Documentation improvements
- 🧪 Test coverage expansion

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fantasy Premier League API** for providing comprehensive player data
- **Streamlit** for the amazing web app framework  
- **Plotly** for beautiful interactive visualizations
- **PuLP** for linear programming optimization
- **Pandas & NumPy** for data manipulation capabilities
- **XGBoost & scikit-learn** for machine learning tools

---

**⭐ If you find this project helpful, please give it a star!**

**🔗 Connect with me:** [GitHub](https://github.com/ataullahkhanrifat) | [LinkedIn](https://linkedin.com/in/ataullahkhanrifat)

