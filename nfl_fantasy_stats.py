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

    print("Generating sample NFL data for demonstration...")

    # Sample teams
    teams = ['KC', 'BUF', 'SF', 'DAL', 'PHI', 'MIA', 'BAL', 'DET']

    # Sample players
    sample_players = []
    sample_stats = []

    # Sample QBs
    qbs = [
        ('Patrick Mahomes', 'KC', 15), ('Josh Allen', 'BUF', 17),
        ('Jalen Hurts', 'PHI', 1), ('Dak Prescott', 'DAL', 4)
    ]

    # Sample RBs
    rbs = [
        ('Christian McCaffrey', 'SF', 23), ('Derrick Henry', 'BAL', 22),
        ('Saquon Barkley', 'PHI', 26), ('Josh Jacobs', 'LV', 8)
    ]

    # Sample WRs
    wrs = [
        ('Tyreek Hill', 'MIA', 10), ('CeeDee Lamb', 'DAL', 88),
        ('Amon-Ra St. Brown', 'DET', 14), ('A.J. Brown', 'PHI', 11)
    ]

    player_id = 1000
    for name, team, jersey in qbs + rbs + wrs:
        pos = 'QB' if name in [q[0] for q in qbs] else 'RB' if name in [r[0] for r in rbs] else 'WR'

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
        else:  # WR
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
