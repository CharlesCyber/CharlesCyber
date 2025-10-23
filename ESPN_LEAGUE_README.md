# ESPN Fantasy Football League Data Scraper

A Python script to extract data from ESPN Fantasy Football leagues and export to CSV files.

## Features

- Fetches team standings and records
- Exports all team rosters with player information
- Retrieves matchup data for any week or all weeks
- Supports both public and private leagues
- Configurable league ID and year
- Exports data to multiple CSV files for easy analysis

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install just the ESPN API:

```bash
pip install espn-api
```

## Usage

### Basic Usage (Public League)

```bash
python espn_league_scraper.py --league-id 428501878
```

### Specify Year

```bash
python espn_league_scraper.py --league-id 428501878 --year 2024
```

### Get Specific Week Matchups

```bash
python espn_league_scraper.py --league-id 428501878 --week 5
```

### Private League (Requires Authentication)

For private leagues, you need to provide your ESPN S2 and SWID cookies:

```bash
python espn_league_scraper.py --league-id 428501878 --espn-s2 "YOUR_ESPN_S2" --swid "YOUR_SWID"
```

#### How to Get ESPN S2 and SWID Cookies

1. Log in to your ESPN Fantasy Football account in a web browser
2. Open Developer Tools (F12 or Right-click > Inspect)
3. Go to the "Application" or "Storage" tab
4. Under "Cookies", select the ESPN domain
5. Find and copy the values for:
   - `espn_s2` (a long string)
   - `SWID` (looks like `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`)

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--league-id` | ESPN league ID | 428501878 |
| `--year` | Season year | Current year |
| `--espn-s2` | ESPN S2 cookie for private leagues | None |
| `--swid` | ESPN SWID cookie for private leagues | None |
| `--week` | Specific week for matchup data | Current week |

## Output Files

The script generates the following CSV files:

1. **espn_teams.csv** - Team standings with wins, losses, points for/against
2. **espn_rosters.csv** - All players on each team with their stats
3. **espn_all_matchups.csv** - All matchups from all weeks played
4. **espn_matchups_week{N}.csv** - Matchups for a specific week (if --week is specified)
5. **espn_league_info.json** - League settings and metadata

## CSV File Structures

### espn_teams.csv
- team_id
- team_name
- owner
- wins
- losses
- ties
- points_for
- points_against
- standing
- playoff_pct

### espn_rosters.csv
- team_id
- team_name
- player_name
- position
- pro_team
- injured
- injury_status
- total_points
- projected_total_points
- avg_points

### espn_all_matchups.csv
- week
- home_team
- home_team_id
- home_score
- away_team
- away_team_id
- away_score

## Examples

### Change League ID

To use a different league, simply change the `--league-id` parameter:

```bash
python espn_league_scraper.py --league-id 123456789
```

### Get Historical Data

```bash
python espn_league_scraper.py --league-id 428501878 --year 2023
```

### Analyze Specific Week

```bash
python espn_league_scraper.py --league-id 428501878 --week 10
```

## Troubleshooting

### "Failed to connect to league"

This usually means:
1. The league ID is incorrect
2. The league is private and requires authentication (provide --espn-s2 and --swid)
3. The year is incorrect or data isn't available for that year

### "espn_api library not available"

Run: `pip install espn-api`

### Private League Access Issues

Make sure you're logged into ESPN in your browser and have copied the correct cookie values. The cookies may expire after some time.

## Notes

- Default league ID is set to 428501878 (can be changed via command line)
- The script fetches data for the current year by default
- All CSV files use UTF-8 encoding
- The script automatically detects the current week for matchup data
- For private leagues, authentication cookies are required

## Credits

Built using the [espn-api](https://github.com/cwendt94/espn-api) Python library.
