# NFL Fantasy Football Stats Scraper

A Python script that fetches current NFL players and their fantasy football statistics using ESPN's public API.

## Features

- Fetches all current NFL players from all 32 teams
- Collects player information (name, position, team, jersey number, etc.)
- Retrieves fantasy football statistics for skill positions
- Exports data to CSV files for easy analysis

## Installation

1. Install Python 3.7 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python nfl_fantasy_stats.py
```

The script will:
1. Fetch all NFL teams
2. Fetch rosters for each team
3. Save player data to `nfl_players.csv`
4. Fetch fantasy statistics for relevant positions (QB, RB, WR, TE, K)
5. Save fantasy stats to `nfl_fantasy_stats.csv`

## Output Files

### nfl_players.csv
Contains all NFL players with the following columns:
- player_id
- name
- position
- jersey
- team
- team_id
- age
- height
- weight
- experience

### nfl_fantasy_stats.csv
Contains fantasy statistics for skill position players:
- player_id
- name
- team
- position
- season
- games_played
- passing_yards
- passing_tds
- interceptions
- rushing_yards
- rushing_tds
- receptions
- receiving_yards
- receiving_tds
- fumbles
- two_point_conversions

## Customization

You can modify the script to:
- Change the season year (default is current year)
- Filter specific positions
- Add additional statistics
- Change output filename

Example - Get stats for 2023 season:
```python
scraper.get_fantasy_stats_for_all_players(season='2023')
```

## Notes

- The script uses Sleeper's public API endpoints
- Data fetching may take a few minutes depending on your connection
- Some players may not have statistics if they haven't played in the current season
- The script includes fallback to sample data if API access is restricted
- When live data is available, you'll get 1500+ active NFL players

## Data Sources

The script uses the Sleeper API (https://api.sleeper.app), which is:
- Free and public
- Designed for fantasy football applications
- No authentication required
- Updated regularly with current NFL data

## Troubleshooting

### API Access Issues (403 Forbidden)
If you see "Unable to fetch live data from API":
- Your network may have firewall/proxy restrictions
- Some corporate or institutional networks block external API calls
- The script will automatically generate sample data for demonstration

**To get live data:**
1. Run the script on a personal computer with unrestricted internet
2. Try running from a different network
3. Check if you're behind a corporate firewall/proxy

### Sample Data Mode
When API access is blocked, the script generates realistic sample data including:
- 12 sample NFL players (4 QBs, 4 RBs, 4 WRs)
- Realistic fantasy statistics
- Properly formatted CSV files for testing

### Other Issues
- Ensure you have the latest version of the `requests` library: `pip install --upgrade requests`
- The Sleeper API may occasionally be down for maintenance
- Check your Python version (requires 3.7+)

## License

Free to use for personal projects and fantasy football analysis.
