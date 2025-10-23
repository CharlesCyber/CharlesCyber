#!/usr/bin/env python3
"""
NFL Fantasy Football Stats Scraper
Fetches current NFL players and their fantasy football statistics
"""

import requests
import csv
import json
from datetime import datetime
from typing import List, Dict, Any


class NFLFantasyStatsScraper:
    """Scraper for NFL player data and fantasy statistics"""

    def __init__(self):
        self.players = []
        self.fantasy_stats = []
        # Using Sleeper API (fantasy-friendly, no auth required)
        self.sleeper_base_url = "https://api.sleeper.app/v1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.player_data_cache = {}

    def fetch_all_nfl_players(self) -> Dict[str, Any]:
        """Fetch all NFL players from Sleeper API"""
        try:
            url = f"{self.sleeper_base_url}/players/nfl"
            print("Fetching all NFL players from Sleeper API...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            print(f"Successfully fetched {len(data)} players")
            return data
        except Exception as e:
            print(f"Error fetching players: {e}")
            return {}

    def fetch_all_players(self) -> List[Dict[str, Any]]:
        """Parse and organize all current NFL players"""
        players_dict = self.fetch_all_nfl_players()

        if not players_dict:
            print("No player data available")
            return []

        all_players = []
        print("Processing player data...")

        for player_id, player_info in players_dict.items():
            # Filter for active NFL players
            if player_info.get('active', False) and player_info.get('sport') == 'nfl':
                player_data = {
                    'player_id': player_id,
                    'name': f"{player_info.get('first_name', '')} {player_info.get('last_name', '')}".strip(),
                    'position': player_info.get('position', ''),
                    'jersey': player_info.get('number', ''),
                    'team': player_info.get('team', 'FA'),
                    'age': player_info.get('age', ''),
                    'height': player_info.get('height', ''),
                    'weight': player_info.get('weight', ''),
                    'college': player_info.get('college', ''),
                    'years_exp': player_info.get('years_exp', 0),
                    'status': player_info.get('status', ''),
                    'injury_status': player_info.get('injury_status', ''),
                }
                all_players.append(player_data)

        self.players = all_players
        self.player_data_cache = players_dict
        print(f"\nTotal active NFL players: {len(all_players)}")
        return all_players

    def fetch_season_stats(self, season: str = '2024', week: str = None) -> Dict[str, Any]:
        """Fetch stats for all players for a given season/week from Sleeper"""
        try:
            # Sleeper API for weekly stats
            # If no week specified, try to get latest week or season totals
            if week:
                url = f"{self.sleeper_base_url}/stats/nfl/regular/{season}/{week}"
            else:
                url = f"{self.sleeper_base_url}/stats/nfl/regular/{season}"

            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Note: Could not fetch stats for season {season}: {e}")
            return {}

    def get_fantasy_stats_for_all_players(self, season: str = '2024'):
        """Fetch fantasy stats for all players"""
        if not self.players:
            print("No players loaded. Please run fetch_all_players() first.")
            return

        print(f"\nFetching fantasy stats from Sleeper API for season {season}...")

        # Fetch season stats (this contains aggregated stats for all players)
        # Try to get season stats - Sleeper may have them aggregated
        all_stats = self.fetch_season_stats(season)

        if not all_stats:
            print("Could not fetch season stats. Using player data only.")
            all_stats = {}

        fantasy_data = []

        # Focus on skill positions that have fantasy relevance
        relevant_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']

        for player in self.players:
            position = player.get('position', '')

            if position not in relevant_positions:
                continue

            player_id = player.get('player_id')
            # Get stats for this specific player
            player_stats = all_stats.get(player_id, {})

            fantasy_record = {
                'player_id': player_id,
                'name': player.get('name'),
                'team': player.get('team'),
                'position': position,
                'season': season,
                'games_played': player_stats.get('gp', 0),
                # Passing stats
                'passing_attempts': player_stats.get('pass_att', 0),
                'passing_completions': player_stats.get('pass_cmp', 0),
                'passing_yards': player_stats.get('pass_yd', 0),
                'passing_tds': player_stats.get('pass_td', 0),
                'interceptions': player_stats.get('pass_int', 0),
                # Rushing stats
                'rushing_attempts': player_stats.get('rush_att', 0),
                'rushing_yards': player_stats.get('rush_yd', 0),
                'rushing_tds': player_stats.get('rush_td', 0),
                # Receiving stats
                'targets': player_stats.get('rec_tgt', 0),
                'receptions': player_stats.get('rec', 0),
                'receiving_yards': player_stats.get('rec_yd', 0),
                'receiving_tds': player_stats.get('rec_td', 0),
                # Other
                'fumbles': player_stats.get('fum', 0),
                'fumbles_lost': player_stats.get('fum_lost', 0),
                # Fantasy points (if available)
                'fantasy_points_ppr': player_stats.get('pts_ppr', 0),
                'fantasy_points_half_ppr': player_stats.get('pts_half_ppr', 0),
                'fantasy_points_std': player_stats.get('pts_std', 0),
            }

            fantasy_data.append(fantasy_record)

        self.fantasy_stats = fantasy_data
        print(f"Processed fantasy stats for {len(fantasy_data)} players")
        return fantasy_data

    def save_players_to_csv(self, filename: str = 'nfl_players.csv'):
        """Save all players to a CSV file"""
        if not self.players:
            print("No players to save!")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if self.players:
                fieldnames = self.players[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.players)

        print(f"\nSaved {len(self.players)} players to {filename}")

    def save_fantasy_stats_to_csv(self, filename: str = 'nfl_fantasy_stats.csv'):
        """Save fantasy stats to a CSV file"""
        if not self.fantasy_stats:
            print("No fantasy stats to save!")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if self.fantasy_stats:
                fieldnames = self.fantasy_stats[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.fantasy_stats)

        print(f"Saved fantasy stats for {len(self.fantasy_stats)} players to {filename}")


def generate_sample_data():
    """Generate sample data for demonstration purposes"""
    import random

    print("Generating comprehensive NFL data for demonstration...")
    print("Creating dataset with 100+ players across all positions...")

    # All 32 NFL teams
    teams = [
        'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
        'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
        'LAC', 'LAR', 'LV', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
        'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS'
    ]

    # Sample players
    sample_players = []
    sample_stats = []

    # Comprehensive QB list (32+ QBs - at least 1 per team)
    qbs = [
        ('Patrick Mahomes', 'KC', 15), ('Josh Allen', 'BUF', 17), ('Jalen Hurts', 'PHI', 1),
        ('Dak Prescott', 'DAL', 4), ('Joe Burrow', 'CIN', 9), ('Lamar Jackson', 'BAL', 8),
        ('Justin Herbert', 'LAC', 10), ('Trevor Lawrence', 'JAX', 16), ('Brock Purdy', 'SF', 13),
        ('Tua Tagovailoa', 'MIA', 1), ('C.J. Stroud', 'HOU', 7), ('Jordan Love', 'GB', 10),
        ('Jared Goff', 'DET', 16), ('Kirk Cousins', 'ATL', 18), ('Geno Smith', 'SEA', 7),
        ('Baker Mayfield', 'TB', 6), ('Matthew Stafford', 'LAR', 9), ('Russell Wilson', 'PIT', 3),
        ('Anthony Richardson', 'IND', 5), ('Derek Carr', 'NO', 4), ('Kyler Murray', 'ARI', 1),
        ('Bryce Young', 'CAR', 9), ('Aaron Rodgers', 'NYJ', 8), ('Daniel Jones', 'NYG', 8),
        ('Deshaun Watson', 'CLE', 4), ('Sam Howell', 'WAS', 14), ('Will Levis', 'TEN', 8),
        ('Jacoby Brissett', 'NE', 7), ('Aidan O\'Connell', 'LV', 12), ('Bo Nix', 'DEN', 10),
        ('Justin Fields', 'PIT', 2), ('Caleb Williams', 'CHI', 18)
    ]

    # Comprehensive RB list (60+ RBs)
    rbs = [
        ('Christian McCaffrey', 'SF', 23), ('Derrick Henry', 'BAL', 22), ('Saquon Barkley', 'PHI', 26),
        ('Breece Hall', 'NYJ', 20), ('Bijan Robinson', 'ATL', 7), ('Jahmyr Gibbs', 'DET', 26),
        ('Travis Etienne', 'JAX', 1), ('Josh Jacobs', 'GB', 8), ('Kenneth Walker', 'SEA', 9),
        ('Alvin Kamara', 'NO', 41), ('Joe Mixon', 'HOU', 28), ('David Montgomery', 'DET', 5),
        ('Isiah Pacheco', 'KC', 10), ('De\'Von Achane', 'MIA', 28), ('Rachaad White', 'TB', 29),
        ('James Conner', 'ARI', 6), ('Kyren Williams', 'LAR', 23), ('Tony Pollard', 'TEN', 20),
        ('Raheem Mostert', 'MIA', 31), ('Najee Harris', 'PIT', 22), ('D\'Andre Swift', 'CHI', 4),
        ('Rhamondre Stevenson', 'NE', 38), ('Jonathan Taylor', 'IND', 28), ('Aaron Jones', 'MIN', 33),
        ('Javonte Williams', 'DEN', 33), ('James Cook', 'BUF', 4), ('Zack Moss', 'CIN', 23),
        ('Jerome Ford', 'CLE', 34), ('Chuba Hubbard', 'CAR', 30), ('Brian Robinson', 'WAS', 8),
        ('Zamir White', 'LV', 35), ('Gus Edwards', 'LAC', 35), ('Tyjae Spears', 'TEN', 2),
        ('Ezekiel Elliott', 'DAL', 15), ('Antonio Gibson', 'NE', 14), ('Miles Sanders', 'CAR', 10),
        ('Khalil Herbert', 'CHI', 24), ('Tyler Allgeier', 'ATL', 25), ('Dameon Pierce', 'HOU', 31),
        ('AJ Dillon', 'GB', 28), ('Cordarrelle Patterson', 'PIT', 84), ('Latavius Murray', 'BUF', 28),
        ('Zach Charbonnet', 'SEA', 26), ('Roschon Johnson', 'CHI', 23), ('Tank Bigsby', 'JAX', 4),
        ('Trey Sermon', 'IND', 28), ('Craig Reynolds', 'DET', 46), ('Devin Singletary', 'NYG', 26),
        ('Damien Harris', 'BUF', 37), ('Samaje Perine', 'DEN', 25), ('Justice Hill', 'BAL', 43),
        ('Alexander Mattison', 'LV', 33), ('Clyde Edwards-Helaire', 'KC', 25), ('Ke\'Shawn Vaughn', 'TB', 21),
        ('Chase Edmonds', 'TB', 22), ('Joshua Kelley', 'LAC', 27), ('Ty Johnson', 'BUF', 25),
        ('Michael Carter', 'ARI', 32), ('Elijah Mitchell', 'SF', 25), ('Cam Akers', 'MIN', 23),
        ('Jamaal Williams', 'NO', 30), ('Kareem Hunt', 'CLE', 27), ('Melvin Gordon', 'BAL', 25)
    ]

    # Comprehensive WR list (80+ WRs)
    wrs = [
        ('Tyreek Hill', 'MIA', 10), ('CeeDee Lamb', 'DAL', 88), ('Amon-Ra St. Brown', 'DET', 14),
        ('A.J. Brown', 'PHI', 11), ('Justin Jefferson', 'MIN', 18), ('Ja\'Marr Chase', 'CIN', 1),
        ('Stefon Diggs', 'HOU', 1), ('Davante Adams', 'LV', 17), ('Puka Nacua', 'LAR', 17),
        ('Nico Collins', 'HOU', 12), ('Garrett Wilson', 'NYJ', 5), ('Brandon Aiyuk', 'SF', 11),
        ('DK Metcalf', 'SEA', 14), ('DeVonta Smith', 'PHI', 6), ('Cooper Kupp', 'LAR', 10),
        ('Mike Evans', 'TB', 13), ('Chris Olave', 'NO', 12), ('DJ Moore', 'CHI', 2),
        ('Deebo Samuel', 'SF', 19), ('Keenan Allen', 'CHI', 13), ('Calvin Ridley', 'TEN', 0),
        ('Amari Cooper', 'CLE', 2), ('Jaylen Waddle', 'MIA', 17), ('Terry McLaurin', 'WAS', 17),
        ('Christian Kirk', 'JAX', 13), ('Diontae Johnson', 'CAR', 5), ('Marquise Brown', 'KC', 5),
        ('Drake London', 'ATL', 5), ('Chris Godwin', 'TB', 14), ('DeAndre Hopkins', 'TEN', 10),
        ('Michael Pittman', 'IND', 11), ('Zay Flowers', 'BAL', 4), ('George Pickens', 'PIT', 14),
        ('Jakobi Meyers', 'LV', 16), ('Tyler Lockett', 'SEA', 16), ('Courtland Sutton', 'DEN', 14),
        ('Jordan Addison', 'MIN', 3), ('Rashee Rice', 'KC', 4), ('Tank Dell', 'HOU', 3),
        ('Jaxon Smith-Njigba', 'SEA', 11), ('Jameson Williams', 'DET', 9), ('Quentin Johnston', 'LAC', 1),
        ('Rashid Shaheed', 'NO', 22), ('Joshua Palmer', 'LAC', 5), ('Romeo Doubs', 'GB', 87),
        ('Darnell Mooney', 'ATL', 1), ('Curtis Samuel', 'BUF', 10), ('Jerry Jeudy', 'CLE', 3),
        ('Gabe Davis', 'JAX', 13), ('Brandin Cooks', 'DAL', 3), ('Michael Thomas', 'NO', 13),
        ('Tyler Boyd', 'TEN', 83), ('Elijah Moore', 'CLE', 8), ('Kadarius Toney', 'KC', 19),
        ('K.J. Osborn', 'NE', 17), ('Marquez Valdes-Scantling', 'BUF', 11), ('Mecole Hardman', 'KC', 12),
        ('Van Jefferson', 'PIT', 19), ('Treylon Burks', 'TEN', 16), ('Skyy Moore', 'KC', 24),
        ('Wan\'Dale Robinson', 'NYG', 17), ('Josh Downs', 'IND', 1), ('Jayden Reed', 'GB', 11),
        ('Michael Wilson', 'ARI', 14), ('Rondale Moore', 'ARI', 4), ('Marvin Mims', 'DEN', 19),
        ('Jonathan Mingo', 'CAR', 15), ('Demario Douglas', 'NE', 81), ('Tutu Atwell', 'LAR', 15),
        ('Xavier Legette', 'CAR', 17), ('Ricky Pearsall', 'SF', 14), ('Ladd McConkey', 'LAC', 15),
        ('Keon Coleman', 'BUF', 0), ('Rome Odunze', 'CHI', 15), ('Brian Thomas Jr', 'JAX', 7),
        ('Adonai Mitchell', 'IND', 10), ('Xavier Worthy', 'KC', 1), ('Malachi Corley', 'NYJ', 14),
        ('Malik Nabers', 'NYG', 1), ('Marvin Harrison Jr', 'ARI', 18), ('Allen Lazard', 'NYJ', 10)
    ]

    # Comprehensive TE list (40+ TEs)
    tes = [
        ('Travis Kelce', 'KC', 87), ('Sam LaPorta', 'DET', 87), ('Mark Andrews', 'BAL', 89),
        ('George Kittle', 'SF', 85), ('T.J. Hockenson', 'MIN', 87), ('Evan Engram', 'JAX', 17),
        ('Kyle Pitts', 'ATL', 8), ('David Njoku', 'CLE', 85), ('Dallas Goedert', 'PHI', 88),
        ('Darren Waller', 'NYG', 12), ('Dalton Kincaid', 'BUF', 86), ('Jake Ferguson', 'DAL', 87),
        ('Cole Kmet', 'CHI', 85), ('Pat Freiermuth', 'PIT', 88), ('Tyler Conklin', 'NYJ', 83),
        ('Taysom Hill', 'NO', 7), ('Hunter Henry', 'NE', 85), ('Jonnu Smith', 'MIA', 9),
        ('Dalton Schultz', 'HOU', 86), ('Chigoziem Okonkwo', 'TEN', 85), ('Juwan Johnson', 'NO', 83),
        ('Luke Musgrave', 'GB', 88), ('Michael Mayer', 'LV', 87), ('Zach Ertz', 'WAS', 86),
        ('Noah Fant', 'SEA', 87), ('Hayden Hurst', 'LAC', 88), ('Tyler Higbee', 'LAR', 89),
        ('Gerald Everett', 'CHI', 81), ('Cade Otton', 'TB', 88), ('Isaiah Likely', 'BAL', 80),
        ('Tucker Kraft', 'GB', 85), ('Brock Bowers', 'LV', 89), ('Trey McBride', 'ARI', 85),
        ('Ja\'Tavion Sanders', 'CAR', 87), ('Theo Johnson', 'NYG', 85), ('Ben Sinnott', 'WAS', 87),
        ('Erick All', 'CIN', 83), ('Brenton Strange', 'JAX', 83), ('Luke Schoonmaker', 'DAL', 86),
        ('Will Dissly', 'LAC', 89), ('Irv Smith Jr', 'HOU', 81), ('Mo Alie-Cox', 'IND', 81)
    ]

    player_id = 1000
    for name, team, jersey in qbs + rbs + wrs + tes:
        if name in [q[0] for q in qbs]:
            pos = 'QB'
        elif name in [r[0] for r in rbs]:
            pos = 'RB'
        elif name in [w[0] for w in wrs]:
            pos = 'WR'
        else:
            pos = 'TE'

        player_data = {
            'player_id': str(player_id),
            'name': name,
            'position': pos,
            'jersey': str(jersey),
            'team': team,
            'age': random.randint(23, 32),
            'height': f"{random.randint(69, 78)}\"",
            'weight': f"{random.randint(185, 250)} lbs",
            'college': 'Sample College',
            'years_exp': random.randint(1, 10),
            'status': 'Active',
            'injury_status': '',
        }
        sample_players.append(player_data)

        # Generate stats based on position
        if pos == 'QB':
            stat_data = {
                'player_id': str(player_id),
                'name': name,
                'team': team,
                'position': pos,
                'season': '2024',
                'games_played': random.randint(14, 17),
                'passing_attempts': random.randint(400, 600),
                'passing_completions': random.randint(280, 420),
                'passing_yards': random.randint(3500, 5000),
                'passing_tds': random.randint(25, 45),
                'interceptions': random.randint(5, 15),
                'rushing_attempts': random.randint(30, 80),
                'rushing_yards': random.randint(200, 600),
                'rushing_tds': random.randint(2, 8),
                'targets': 0,
                'receptions': 0,
                'receiving_yards': 0,
                'receiving_tds': 0,
                'fumbles': random.randint(0, 3),
                'fumbles_lost': random.randint(0, 2),
                'fantasy_points_ppr': round(random.uniform(280, 380), 2),
                'fantasy_points_half_ppr': round(random.uniform(270, 370), 2),
                'fantasy_points_std': round(random.uniform(260, 360), 2),
            }
        elif pos == 'RB':
            stat_data = {
                'player_id': str(player_id),
                'name': name,
                'team': team,
                'position': pos,
                'season': '2024',
                'games_played': random.randint(12, 17),
                'passing_attempts': 0,
                'passing_completions': 0,
                'passing_yards': 0,
                'passing_tds': 0,
                'interceptions': 0,
                'rushing_attempts': random.randint(180, 320),
                'rushing_yards': random.randint(900, 1800),
                'rushing_tds': random.randint(6, 18),
                'targets': random.randint(30, 90),
                'receptions': random.randint(25, 75),
                'receiving_yards': random.randint(200, 800),
                'receiving_tds': random.randint(1, 6),
                'fumbles': random.randint(0, 3),
                'fumbles_lost': random.randint(0, 2),
                'fantasy_points_ppr': round(random.uniform(180, 350), 2),
                'fantasy_points_half_ppr': round(random.uniform(170, 330), 2),
                'fantasy_points_std': round(random.uniform(150, 300), 2),
            }
        elif pos == 'WR':
            stat_data = {
                'player_id': str(player_id),
                'name': name,
                'team': team,
                'position': pos,
                'season': '2024',
                'games_played': random.randint(14, 17),
                'passing_attempts': 0,
                'passing_completions': 0,
                'passing_yards': 0,
                'passing_tds': 0,
                'interceptions': 0,
                'rushing_attempts': random.randint(0, 15),
                'rushing_yards': random.randint(0, 100),
                'rushing_tds': random.randint(0, 2),
                'targets': random.randint(100, 180),
                'receptions': random.randint(70, 130),
                'receiving_yards': random.randint(900, 1800),
                'receiving_tds': random.randint(6, 15),
                'fumbles': random.randint(0, 2),
                'fumbles_lost': random.randint(0, 1),
                'fantasy_points_ppr': round(random.uniform(200, 370), 2),
                'fantasy_points_half_ppr': round(random.uniform(180, 340), 2),
                'fantasy_points_std': round(random.uniform(160, 310), 2),
            }
        else:  # TE
            stat_data = {
                'player_id': str(player_id),
                'name': name,
                'team': team,
                'position': pos,
                'season': '2024',
                'games_played': random.randint(14, 17),
                'passing_attempts': 0,
                'passing_completions': 0,
                'passing_yards': 0,
                'passing_tds': 0,
                'interceptions': 0,
                'rushing_attempts': 0,
                'rushing_yards': 0,
                'rushing_tds': 0,
                'targets': random.randint(80, 150),
                'receptions': random.randint(60, 110),
                'receiving_yards': random.randint(700, 1400),
                'receiving_tds': random.randint(4, 12),
                'fumbles': random.randint(0, 2),
                'fumbles_lost': random.randint(0, 1),
                'fantasy_points_ppr': round(random.uniform(160, 280), 2),
                'fantasy_points_half_ppr': round(random.uniform(140, 250), 2),
                'fantasy_points_std': round(random.uniform(120, 220), 2),
            }

        sample_stats.append(stat_data)
        player_id += 1

    return sample_players, sample_stats


def main():
    """Main execution function"""
    print("=" * 60)
    print("NFL Fantasy Football Stats Scraper")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    scraper = NFLFantasyStatsScraper()

    # Step 1: Fetch all NFL players
    print("Step 1: Fetching all current NFL players...")
    scraper.fetch_all_players()

    # If no data was fetched (API blocked), use sample data
    if not scraper.players:
        print("\n" + "!" * 60)
        print("Unable to fetch live data from API.")
        print("This may be due to network restrictions or API blocking.")
        print("Generating sample data for demonstration purposes...")
        print("!" * 60 + "\n")

        sample_players, sample_stats = generate_sample_data()
        scraper.players = sample_players
        scraper.fantasy_stats = sample_stats

    # Step 2: Save players to CSV
    print("\nStep 2: Saving players to CSV...")
    scraper.save_players_to_csv('nfl_players.csv')

    # Step 3: Fetch fantasy stats (if not using sample data)
    if scraper.fantasy_stats:
        print("\nStep 3: Using existing fantasy statistics...")
    else:
        print("\nStep 3: Fetching fantasy football statistics...")
        current_season = datetime.now().year
        scraper.get_fantasy_stats_for_all_players(season=str(current_season))

    # Step 4: Save fantasy stats to CSV
    print("\nStep 4: Saving fantasy stats to CSV...")
    scraper.save_fantasy_stats_to_csv('nfl_fantasy_stats.csv')

    print("\n" + "=" * 60)
    print("Process complete!")
    print("=" * 60)
    print(f"Output files:")
    print(f"  - nfl_players.csv ({len(scraper.players)} players)")
    print(f"  - nfl_fantasy_stats.csv ({len(scraper.fantasy_stats)} players)")
    print("\nNote: If you see sample data, run this script in an environment")
    print("with unrestricted internet access to fetch live NFL data.")


if __name__ == "__main__":
    main()
