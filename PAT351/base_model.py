import argparse
import json
from collections import defaultdict
import os

def get_shot_fields(current_shot):
    # maps the data given to their corresponding indices after splitting with _ 
    data_indices = {"player_idx": 0, "court_idx": 2, "handedness_idx": 3, "shot_idx": 4, "shot_direction_idx": 5, "formation_idx":6, "outcome_idx": -1}
    label_parts = current_shot['event'].split('_')
    isFH = "forehand" in label_parts[data_indices["handedness_idx"]]
    player = label_parts[data_indices["player_idx"]]
    shot = label_parts[data_indices["shot_idx"]].replace('-', '')
    court = label_parts[data_indices["court_idx"]][:2]  # e.g., 'de' or 'ad'
    outcome = label_parts[data_indices["outcome_idx"]]
    formation = label_parts[data_indices["formation_idx"]]
    if 'serve' not in shot:
        side = "FH" if isFH else "BH"
    else:
        side = ''
    return player, shot.capitalize(), court.capitalize(), side, outcome, formation

def parse_shot_data(json_file):
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Initialize a dictionary to hold shot type counts for each successor state
    shot_counts = defaultdict(lambda: defaultdict(int))

    # Loop through each match entry in the JSON file
    for rally in data['rallies']:
        events = rally['events']
        # Iterate through events in pairs to capture shot type and its successor state
        for i in range(len(events)):
            current_shot = events[i]
            # Extract player, court, shot type, and outcome from the current shot
            player, shot, court, side, outcome, _ = get_shot_fields(current_shot)
            
            # Create the shot type key
            if 'serve' in shot.lower():
                shot_type = f"{player}_{court.capitalize()}{shot}"
            else:
                shot_type = f"{player}_{court.capitalize()}{shot.capitalize()}_{side.upper()}"
            if i + 1 < len(events):
                next_shot = events[i + 1]
            # Get the outcome/next state of the shot (e.g., P3_DeReturn_BH, Error, Ace, etc.)
            if outcome == 'err' and shot != "Serve":
                next_state = 'Error'
            elif outcome == 'win':
                next_state = 'Win'
            else:
                next_player, next_shot_type, next_court, next_side, outcome, _ = get_shot_fields(next_shot)
                if 'serve' in next_shot_type.lower():
                    next_state = f"{next_player}_{next_court.capitalize()}{next_shot_type.capitalize()}"
                else:
                    next_state = f"{next_player}_{next_court.capitalize()}{next_shot_type.capitalize()}_{next_side.upper()}"

            # Increment the count for this shot type and successor state
            shot_counts[shot_type][next_state] += 1

    return shot_counts

def merge_dicts(dict1, dict2):
    # Initialize the resulting dictionary
    merged_dict = dict1.copy()  # Start with a copy of dict1 to avoid modifying the original
    # Iterate over dict2's items
    for key, value in dict2.items():
        if key in merged_dict:
            # If the value is a dictionary, we recursively combine.
            if isinstance(value, dict):
                merged_dict[key] = merge_dicts(value, merged_dict[key])
            else:
                # If value is simply an integer count, we add the counts
                merged_dict[key] += value
        else:
            merged_dict[key] = value
    
    return merged_dict

def eval_pcsp(file_name):
    # os.system('cp %s ../PAT351/%s' % (os.path.join(dir, file_name), file_name))
    # os.chdir('PAT351')
    os.system('mono PAT3.Console.exe -pcsp %s %s.txt' % (file_name, file_name[:-5]))
    with open('%s.txt' % file_name[:-5]) as f:
        lines = f.readlines()
    # os.system('rm %s' % file_name)
    # os.system('rm %s.txt' % file_name[:-5])
    os.chdir('..')
    if len(lines) < 5 or '[' not in lines[3] or ']' not in lines[3]:
        print(lines)
        return -1, -1
    print(lines[3])
    min_max_probs = [float(score) for score in lines[3].split('[')[1].split(']')[0].split(',')]
    return min_max_probs


def generate_pcsp(counts_dict):
    output = '#include "new_env.pcsp";\n'
    for key, value in counts_dict.items():
        player = key[1]
        output += "%s = %sReady -> pcase { \n" % (key, key) 
        
        # Sort the inner dictionary by value (count) in descending order
        sorted_actions = sorted(value.items(), key=lambda x: x[1], reverse=True)
        
        for action, count in sorted_actions:
            if 'Error' in action:
                output += f"\t{count}: {key}_err -> Error{{call(awardPoint, {player}, true)}} -> NextPt\n" 
            elif 'Win' in action:
                output += f"\t{count}: {key}_win -> Winner{{call(awardPoint, {player}, false)}} -> NextPt\n"
            else:
                output += f"\t{count}: {action}\n"
        
        output += "};\n"
    assertions = '''#define Team1Win won==t1;\n#define Team2Win won==t2;\n#assert TieBreakGame reaches Team1Win with prob;\n#assert TieBreakGame reaches Team2Win with prob;'''
    output += assertions
    output_filename = 'base_output.pcsp'
    with open(output_filename, 'w') as f:
        f.write(output)
    return output_filename
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', type=str, nargs='+', help="JSON file names")
    args = parser.parse_args()
    full_data = {}
    env_file = "doubles_env.pcsp"
    for json_file in args.json:
        shot_data = parse_shot_data(json_file)
        full_data = merge_dicts(full_data, shot_data)
    # print(full_data)
    print(eval_pcsp(generate_pcsp(full_data)))