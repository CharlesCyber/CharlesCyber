#!/usr/bin/env python3
"""
ESPN Fantasy Football League Data Scraper
Fetches league data from ESPN Fantasy Football and exports to CSV
"""

import argparse
import csv
import json
from datetime import datetime
from typing import List, Dict, Any

try:
    from espn_api.football import League
    ESPN_API_AVAILABLE = True
except ImportError:
    ESPN_API_AVAILABLE = False
    print("Warning: espn_api not installed. Install with: pip install espn-api")


class ESPNLeagueScraper:
    """Scraper for ESPN Fantasy Football league data"""

    def __init__(self, league_id: int, year: int = None, espn_s2: str = None, swid: str = None):
        """
        Initialize the ESPN League Scraper

        Args:
            league_id: ESPN league ID
            year: Season year (defaults to current year)
            espn_s2: ESPN S2 cookie (required for private leagues)
            swid: ESPN SWID cookie (required for private leagues)
        """
        self.league_id = league_id
        self.year = year or datetime.now().year
        self.espn_s2 = espn_s2
        self.swid = swid
        self.league = None

        if not ESPN_API_AVAILABLE:
            raise ImportError("espn_api library not available. Install with: pip install espn-api")

    def connect_to_league(self):
        """Connect to the ESPN league"""
        try:
            print(f"Connecting to ESPN league {self.league_id} for year {self.year}...")

            if self.espn_s2 and self.swid:
                # Private league with authentication
                self.league = League(
                    league_id=self.league_id,
                    year=self.year,
                    espn_s2=self.espn_s2,
                    swid=self.swid
                )
                print("Connected to private league with authentication")
            else:
                # Public league
                self.league = League(
                    league_id=self.league_id,
                    year=self.year
                )
                print("Connected to public league")

            print(f"League: {self.league.settings.name}")
            print(f"Teams: {len(self.league.teams)}")
            return True

        except Exception as e:
            print(f"Error connecting to league: {e}")
            print("\nIf this is a private league, you need to provide espn_s2 and swid cookies.")
            print("See README for instructions on how to get these values.")
            return False

    def get_teams_data(self) -> List[Dict[str, Any]]:
        """Extract team information"""
        if not self.league:
            return []

        teams_data = []
        for team in self.league.teams:
            team_info = {
                'team_id': team.team_id,
                'team_name': team.team_name,
                'owner': team.owner,
                'wins': team.wins,
                'losses': team.losses,
                'ties': team.ties,
                'points_for': team.points_for,
                'points_against': team.points_against,
                'standing': team.standing,
                'playoff_pct': team.playoff_pct if hasattr(team, 'playoff_pct') else 0,
            }
            teams_data.append(team_info)

        return teams_data

    def get_rosters_data(self) -> List[Dict[str, Any]]:
        """Extract roster information for all teams"""
        if not self.league:
            return []

        rosters_data = []
        for team in self.league.teams:
            for player in team.roster:
                player_info = {
                    'team_id': team.team_id,
                    'team_name': team.team_name,
                    'player_name': player.name,
                    'position': player.position,
                    'pro_team': player.proTeam,
                    'injured': player.injured,
                    'injury_status': player.injuryStatus if hasattr(player, 'injuryStatus') else '',
                    'total_points': player.total_points if hasattr(player, 'total_points') else 0,
                    'projected_total_points': player.projected_total_points if hasattr(player, 'projected_total_points') else 0,
                    'avg_points': player.avg_points if hasattr(player, 'avg_points') else 0,
                }
                rosters_data.append(player_info)

        return rosters_data

    def get_matchups_data(self, week: int = None) -> List[Dict[str, Any]]:
        """
        Extract matchup information

        Args:
            week: Specific week number (defaults to current week)
        """
        if not self.league:
            return []

        if week is None:
            week = self.league.current_week

        matchups_data = []
        box_scores = self.league.box_scores(week=week)

        for matchup in box_scores:
            matchup_info = {
                'week': week,
                'home_team': matchup.home_team.team_name if matchup.home_team else 'BYE',
                'home_team_id': matchup.home_team.team_id if matchup.home_team else None,
                'home_score': matchup.home_score,
                'away_team': matchup.away_team.team_name if matchup.away_team else 'BYE',
                'away_team_id': matchup.away_team.team_id if matchup.away_team else None,
                'away_score': matchup.away_score,
            }
            matchups_data.append(matchup_info)

        return matchups_data

    def get_league_settings(self) -> Dict[str, Any]:
        """Extract league settings"""
        if not self.league:
            return {}

        settings = self.league.settings

        return {
            'name': settings.name,
            'season': self.year,
            'reg_season_count': settings.reg_season_count,
            'playoff_team_count': settings.playoff_team_count,
            'team_count': settings.team_count,
            'playoff_seed_tie_rule': settings.playoff_seed_tie_rule if hasattr(settings, 'playoff_seed_tie_rule') else '',
            'roster_size': settings.roster_size if hasattr(settings, 'roster_size') else 0,
        }

    def save_teams_to_csv(self, filename: str = 'espn_teams.csv'):
        """Save team data to CSV"""
        teams_data = self.get_teams_data()

        if not teams_data:
            print("No team data to save!")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = teams_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(teams_data)

        print(f"Saved {len(teams_data)} teams to {filename}")

    def save_rosters_to_csv(self, filename: str = 'espn_rosters.csv'):
        """Save roster data to CSV"""
        rosters_data = self.get_rosters_data()

        if not rosters_data:
            print("No roster data to save!")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = rosters_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rosters_data)

        print(f"Saved {len(rosters_data)} roster entries to {filename}")

    def save_matchups_to_csv(self, week: int = None, filename: str = None):
        """Save matchup data to CSV"""
        if week is None:
            week = self.league.current_week if self.league else 1

        if filename is None:
            filename = f'espn_matchups_week{week}.csv'

        matchups_data = self.get_matchups_data(week)

        if not matchups_data:
            print("No matchup data to save!")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = matchups_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matchups_data)

        print(f"Saved {len(matchups_data)} matchups to {filename}")

    def save_all_matchups_to_csv(self, filename: str = 'espn_all_matchups.csv'):
        """Save all matchups from all weeks to CSV"""
        if not self.league:
            print("No league data available!")
            return

        all_matchups = []
        current_week = self.league.current_week

        for week in range(1, current_week + 1):
            matchups = self.get_matchups_data(week)
            all_matchups.extend(matchups)

        if not all_matchups:
            print("No matchup data to save!")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = all_matchups[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_matchups)

        print(f"Saved {len(all_matchups)} total matchups from weeks 1-{current_week} to {filename}")

    def save_league_info_to_json(self, filename: str = 'espn_league_info.json'):
        """Save league settings to JSON"""
        league_info = self.get_league_settings()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(league_info, f, indent=2)

        print(f"Saved league info to {filename}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='ESPN Fantasy Football League Data Scraper')
    parser.add_argument('--league-id', type=int, default=428501878,
                        help='ESPN league ID (default: 428501878)')
    parser.add_argument('--year', type=int, default=None,
                        help='Season year (default: current year)')
    parser.add_argument('--espn-s2', type=str, default=None,
                        help='ESPN S2 cookie for private leagues')
    parser.add_argument('--swid', type=str, default=None,
                        help='ESPN SWID cookie for private leagues')
    parser.add_argument('--week', type=int, default=None,
                        help='Specific week for matchup data (default: current week)')

    args = parser.parse_args()

    print("=" * 60)
    print("ESPN Fantasy Football League Data Scraper")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"League ID: {args.league_id}")
    print(f"Year: {args.year or datetime.now().year}\n")

    if not ESPN_API_AVAILABLE:
        print("\nERROR: espn_api library not installed!")
        print("Please install it with: pip install espn-api")
        print("\nOr install all requirements: pip install -r requirements.txt")
        return

    # Create scraper
    scraper = ESPNLeagueScraper(
        league_id=args.league_id,
        year=args.year,
        espn_s2=args.espn_s2,
        swid=args.swid
    )

    # Connect to league
    if not scraper.connect_to_league():
        print("\nFailed to connect to league. Exiting.")
        return

    print("\n" + "=" * 60)
    print("Extracting Data...")
    print("=" * 60)

    # Save all data to CSV
    print("\n1. Saving team standings...")
    scraper.save_teams_to_csv()

    print("\n2. Saving team rosters...")
    scraper.save_rosters_to_csv()

    print("\n3. Saving all matchups...")
    scraper.save_all_matchups_to_csv()

    if args.week:
        print(f"\n4. Saving matchups for week {args.week}...")
        scraper.save_matchups_to_csv(week=args.week)

    print("\n5. Saving league info...")
    scraper.save_league_info_to_json()

    print("\n" + "=" * 60)
    print("Process complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - espn_teams.csv (team standings)")
    print("  - espn_rosters.csv (all team rosters)")
    print("  - espn_all_matchups.csv (all matchups)")
    if args.week:
        print(f"  - espn_matchups_week{args.week}.csv (week {args.week} matchups)")
    print("  - espn_league_info.json (league settings)")
    print("\nUsage examples:")
    print(f"  python espn_league_scraper.py --league-id {args.league_id}")
    print(f"  python espn_league_scraper.py --league-id {args.league_id} --year 2023")
    print(f"  python espn_league_scraper.py --league-id {args.league_id} --week 5")


if __name__ == "__main__":
    main()
