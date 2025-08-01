# FPL Squad Optimizer ⚽

A comprehensive Fantasy Premier League assistant that uses **machine learning predictions** and **mathematical optimization** to help you build the perfect squad.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

### 🎯 Squad Optimization
- **Advanced Linear Programming**: Uses PuLP optimization for finding optimal 15-player squads
- **Budget Management**: Customizable budget constraints (£80-120m range)
- **Position Requirements**: Enforces proper formation (2 GK, 5 DEF, 5 MID, 3 FWD)
- **Team Diversity**: Maximum 3 players per team rule
- **Manual Controls**: Force include/exclude specific players
- **Cost Efficiency**: Optimizes points per million spent

### 📊 Comprehensive Player Statistics
- **25+ Statistical Categories**: Goals, assists, clean sheets, bonus points, ICT index, and more
- **6 Analysis Tabs**: Top Performers, Attack Stats, Defense Stats, General Stats, Advanced Stats, Team Analysis
- **Professional Data Tables**: Left-aligned formatting with proper styling
- **Interactive Filtering**: Search by player name, team, or position
- **Value Analysis**: Best value players, differential picks, budget options

### 🔮 Next 3 Gameweeks Analysis
- **Fixture Difficulty Rating (FDR)**: Analyzes opponent strength for better player selection
- **Position-Specific Recommendations**: Tailored advice for GK, DEF, MID, FWD
- **Team Performance Metrics**: Form analysis and upcoming fixture difficulty
- **Strategic Insights**: Captain picks and transfer recommendations

### 🌐 Interactive Web Interface
- **Beautiful Streamlit App**: Modern, responsive design with custom CSS
- **Real-time Updates**: Live data fetching from FPL API
- **Multi-page Navigation**: Seamless switching between optimizer, stats, and fixtures
- **Visual Analytics**: Charts, graphs, and interactive tables

## 🏗️ Project Structure

```
F_PL-Project/
├── data/
│   ├── raw/                          # Raw JSON data from FPL API
│   │   ├── fpl_data_latest.json     # Player data and statistics
│   │   └── fpl_fixtures_latest.json # Fixture and team data
│   └── processed/                    # Cleaned CSV data ready for analysis
│       └── fpl_players_latest.csv   # Processed player data with FDR
├── src/
│   ├── fetch_fpl_data.py            # Data fetching with FDR calculations
│   └── optimizer.py                 # Squad optimization engine (CLI)
├── web_app/
│   ├── app.py                       # Main Streamlit application entry point
│   ├── FPL_Squad_Optimizer.py      # Squad optimization page with controls
│   ├── FPL_Player_Statistics.py    # Comprehensive player statistics page
│   ├── Next_3_Gameweeks.py         # Fixture analysis and recommendations
│   └── utils.py                     # Shared utilities and styling functions
├── venv/                            # Virtual environment (auto-created)
├── requirements.txt                 # Production dependencies
├── run.sh                          # Interactive setup and launch script
├── pyproject.toml                  # Project configuration
├── LICENSE                         # MIT license
└── README.md                       # This documentation
```

## 🚀 Quick Start

**One-command interactive setup:**
```bash
./run.sh
```

The script will guide you through:
1. 📊 Fetch fresh FPL data
2. 🧠 Train ML model (Jupyter) 
3. ⚙️ Run optimizer (CLI)
4. 🌐 Launch web app
5. 📝 Show quick demo

**Direct web app launch:**
```bash
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
   python -m venv venv
   source venv/Scripts/activate  # On Windows Git Bash
   # source venv/bin/activate    # On Linux/Mac
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

### 🔮 Fixture Analysis
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
- **Multi-Page Navigation**: Seamless switching between optimizer, stats, and fixtures
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Custom Styling**: Professional appearance with branded colors and fonts
- **Data Validation**: Automatic checks for data quality and availability
- **Error Handling**: Graceful fallbacks when data is unavailable

## 📈 Technical Implementation

### Data Pipeline
- **FPL API Integration**: Direct connection to `https://fantasy.premierleague.com/api/`
- **Data Processing**: Pandas-based cleaning and feature engineering
- **FDR Calculations**: Custom algorithms for fixture difficulty analysis
- **Caching**: Efficient data storage and retrieval

### Optimization Algorithm
- **Objective Function**: Maximize predicted points within constraints
- **Constraint Programming**: Budget, position, and team diversity rules
- **Solver**: PuLP with CBC optimizer for reliable solutions
- **Performance**: Sub-second optimization for most scenarios

### Web Framework
- **Frontend**: Streamlit with custom CSS for professional styling
- **Backend**: Python with pandas for data manipulation
- **Visualization**: Plotly for interactive charts and graphs
- **State Management**: Session-based user preferences and selections

## 🎮 API Usage

This project uses the official Fantasy Premier League API:
- **Endpoint**: `https://fantasy.premierleague.com/api/bootstrap-static/`
- **No authentication required** - Public API access
- **Rate limiting respected** - Responsible data fetching
- **Real-time data** - Live player statistics and prices
- **Comprehensive data** - 800+ players with 40+ features each

## 📊 Sample Output

### 🏆 Optimal Squad Example:
```
💰 BUDGET: £100.0m | SPENT: £99.8m | REMAINING: £0.2m
🎯 PREDICTED POINTS: 1,847 (Season Total)

STARTING XI:
GK  Alisson (£5.5m)           - Liverpool
DEF Alexander-Arnold (£7.1m)   - Liverpool  
DEF Saliba (£5.9m)            - Arsenal
DEF Trippier (£6.2m)          - Newcastle
MID Salah (£13.6m)            - Liverpool
MID De Bruyne (£12.1m)        - Man City
MID Saka (£11.2m)             - Arsenal
MID Palmer (£10.7m)           - Chelsea
FWD Haaland (£14.9m)          - Man City
FWD Watkins (£9.1m)           - Aston Villa
FWD Isak (£8.4m)              - Newcastle

BENCH:
GK  Flekken (£4.6m)           - Brentford
DEF Konsa (£4.8m)             - Aston Villa
MID Luis Díaz (£7.9m)         - Liverpool
FWD Wood (£6.2m)              - Newcastle
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

### 🔮 Fixture Analysis Sample:
```
📅 NEXT 3 GAMEWEEKS ANALYSIS:

GW15: Liverpool (H) vs Brighton
- Attack FDR: 2/5 (Good)
- Defense FDR: 3/5 (Average)
- Recommendation: Strong captain option for Salah

GW16: Arsenal (A) vs Man City  
- Attack FDR: 4/5 (Difficult)
- Defense FDR: 4/5 (Difficult)
- Recommendation: Avoid Arsenal attackers, consider City defense
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
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
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

