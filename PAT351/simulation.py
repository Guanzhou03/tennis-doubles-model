import random

def simulate_game(server_win_prob):
    server_points = 0
    receiver_points = 0
    while True:
        # Simulate a point
        if random.random() < server_win_prob:
            server_points += 1
        else:
            receiver_points += 1

        # Check for game win
        if server_points >= 4 or receiver_points >= 4:
            # Simplified game win condition (since we're not using deuce)
            if abs(server_points - receiver_points) >= 2:
                break
    return server_points > receiver_points

def simulate_tiebreak(P1_serve_win, P2_serve_win, P3_serve_win, P4_serve_win):
    num_matches = 1000
    team1_wins = 0
    error = 0.03
    for match in range(num_matches):
        team1_players = [P1_serve_win + random.uniform(-error, error), P2_serve_win + random.uniform(-error, error)]
        team2_players = [P3_serve_win + random.uniform(-error, error), P4_serve_win + random.uniform(-error, error)]
        random.shuffle(team1_players)  # Randomize serving order within Team 1
        random.shuffle(team2_players)  # Randomize serving order within Team 2

        team1_first = [(1, team1_players[0]), (2, team2_players[0]), (1, team1_players[1]), (2, team2_players[1])]
        team2_first = [(2, team2_players[0]), (1, team1_players[0]), (2, team2_players[1]), (1, team1_players[1])]
        orders = random.choice([team1_first, team2_first])
        points = [0, 0]  # [Team1 points, Team2 points]
        server_idx = 0

        while True:
            # Use modulo to cycle through the players
            serving_team, server_win_prob = orders[server_idx % 4]

            # Simulate the point
            if random.random() < server_win_prob:
                points[serving_team - 1] += 1  # Server's team wins the point
            else:
                points[2 - serving_team] += 1  # Opponent's team wins the point
            if sum(points) % 2 == 1:
                # if odd points then swap
                server_idx += 1

            # Check for tiebreak win conditions
            if (points[0] >= 7 or points[1] >= 7):
                if points[0] > points[1]:
                    team1_wins += 1
                break

    return team1_wins / num_matches  # Return True if Team 1 wins

def simulate_full_game(P1_serve_win, P2_serve_win, P3_serve_win, P4_serve_win):
    # Simulation parameters
    num_matches = 1000
    team1_wins = 0

    # Match format
    sets_to_win = 2  # Best of 3 sets
    games_to_win_set = 6  # First to 6 games
    tiebreak_at = 6  # Tie-break at 6-6

    for match in range(num_matches):
        team1_sets = 0
        team2_sets = 0

        # Randomize which team serves first
        first_serving_team = random.choice([1, 2])

        # Randomize serving order within teams for the match, as well as add deviation for each match
        error = 0.03
        team1_players = [P1_serve_win + random.uniform(-error, error), P2_serve_win + random.uniform(-error, error)]
        team2_players = [P3_serve_win + random.uniform(-error, error), P4_serve_win + random.uniform(-error, error)]

        # Randomize serving order within teams for each set
        team1_serving_order = team1_players.copy()
        team2_serving_order = team2_players.copy()

        while team1_sets < sets_to_win and team2_sets < sets_to_win:
            team1_games = 0
            team2_games = 0

            # Randomize serving order within teams at the start of each set
            random.shuffle(team1_serving_order)
            random.shuffle(team2_serving_order)

            # Create serving order for the set
            if first_serving_team == 1:
                serving_order = [
                    team1_serving_order[0],  # Team 1, Player A
                    team2_serving_order[0],  # Team 2, Player A
                    team1_serving_order[1],  # Team 1, Player B
                    team2_serving_order[1],  # Team 2, Player B
                ]
            else:
                serving_order = [
                    team2_serving_order[0],  # Team 2, Player A
                    team1_serving_order[0],  # Team 1, Player A
                    team2_serving_order[1],  # Team 2, Player B
                    team1_serving_order[1],  # Team 1, Player B
                ]

            server_index = 0  # Start with the first server in the serving_order list

            while True:
                # Get current server's win probability
                server_win_prob = serving_order[server_index % 4]
                serving_team = 1 if (serving_order[server_index % 4] in team1_players) else 2

                # Simulate the game
                server_won = simulate_game(server_win_prob)

                # Update game scores
                if server_won:
                    if serving_team == 1:
                        team1_games += 1
                    else:
                        team2_games += 1
                else:
                    if serving_team == 1:
                        team2_games += 1
                    else:
                        team1_games += 1

                server_index += 1  # Next server

                # Check for set win
                if (team1_games >= games_to_win_set or team2_games >= games_to_win_set) and abs(team1_games - team2_games) >= 2:
                    break

                # Tie-break at 6-6
                if team1_games == tiebreak_at and team2_games == tiebreak_at:
                    # Simulate tie-break
                    tiebreak_winner_team1 = simulate_tiebreak(P1_serve_win, P2_serve_win, P3_serve_win, P4_serve_win)
                    if tiebreak_winner_team1:
                        team1_sets += 1
                    else:
                        team2_sets += 1
                    break  # End of set

            # Update sets won
            if team1_games > team2_games:
                team1_sets += 1
            elif team2_games > team1_games:
                team2_sets += 1
            else:
                # Tie-break winner already updated sets
                pass

            # Alternate which team serves first in the next set
            first_serving_team = 1 if first_serving_team == 2 else 2

        # Update match wins
        if team1_sets > team2_sets:
            team1_wins += 1

    # Calculate and display winning probability
    team1_win_probability = team1_wins / num_matches
    return team1_win_probability