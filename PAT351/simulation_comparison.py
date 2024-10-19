from simulation import *
from formation_model import *
def modify_env_file_to_let_player_serve(player, filename):
    # Read the original file content
    with open(filename, 'r') as file:
        original_lines = file.readlines()
    modified_lines = []

    for line in original_lines:
        # Check if the line contains a key-value pair (e.g., '1:')
        if 'Serve' in line and ':' in line and '->' in line:
            parts = line.strip().split(':', 1)
            key = parts[0].strip()
            rest_of_line = parts[1].strip()

            # Check if the line corresponds to the current player's DeServe or AdServe
            if f'P{player}DeServe' in rest_of_line or f'P{player}AdServe' in rest_of_line:
                new_key = '1'
            else:
                new_key = '0'

            # Reconstruct the line with the new key
            modified_line = f'    {new_key}: {rest_of_line}\n'
            modified_lines.append(modified_line)
        else:
            # If the line doesn't contain a service key-value pair, keep it as is
            modified_lines.append(line)

    # Overwrite the file with the modified content
    with open(filename, 'w') as file:
        file.writelines(modified_lines)

    # print(f"Updated file for Player {player}.")

def calculate_player_serve_winning_chance(player, model, env_file):
    pcsp_file = model.generate_pcsp(env_file)
    team1_win_prob =  model.eval_pcsp(pcsp_file)
    if player <= 2:
        return team1_win_prob
    else:
        return 1 - team1_win_prob

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', type=str, nargs='+', help="JSON file names")
    args = parser.parse_args()

    # Instantiate the Model
    model = FormationModel()

    # Process each JSON file
    for json_file in args.json:
        model.parse_shot_data(json_file)
    player_winning_chances_with_serve = {}
    
    for player in range(1, 5):
        modify_env_file_to_let_player_serve(player, filename="testing.pcsp")
        player_winning_chances_with_serve[player] = calculate_player_serve_winning_chance(
            player, model, env_file='"testing.pcsp"')
    
    one_point_env = '"formation_env.pcsp"'
    print("Team 1 winning chance in full game: ", simulate_full_game(*player_winning_chances_with_serve.values()))
    print("Team 1 winning chance in 1-point game: ", model.eval_pcsp(model.generate_pcsp(one_point_env)))
    print("Team 1 winning chance in 7-point tiebreak:", simulate_tiebreak(*player_winning_chances_with_serve.values()))
    