import json
import os

ELO_FILE = "output/elo_ratings.json"

class EloSystem:
    def __init__(self):
        self._load()

    def _load(self):
        if os.path.exists(ELO_FILE):
            with open(ELO_FILE, 'r') as f:
                self.ratings = json.load(f)
        else:
            self.ratings = {}

    def get_rating(self, agent_name):
        return self.ratings.get(agent_name, 1200) # Default start rating

    def update_ratings(self, agents_list, winner_name):
        """
        Simple ELO update: Winner gains, Losers lose.
        """
        K = 32 # Volatility factor

        for agent in agents_list:
            if agent == winner_name:
                continue
            
            # Calculate Expected Score for Winner vs This Loser
            r_win = self.get_rating(winner_name)
            r_lose = self.get_rating(agent)
            
            expected_win = 1 / (1 + 10 ** ((r_lose - r_win) / 400))
            
            # Update Winner
            self.ratings[winner_name] = round(r_win + K * (1 - expected_win))
            # Update Loser
            self.ratings[agent] = round(r_lose + K * (0 - (1 - expected_win)))

        self._save()

    def _save(self):
        with open(ELO_FILE, 'w') as f:
            json.dump(self.ratings, f, indent=4)
            
    def get_leaderboard(self):
        # Return sorted list
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)