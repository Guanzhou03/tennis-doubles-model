import argparse
import json
from collections import defaultdict
import os

def get_shot_fields(current_shot):
    label_parts = current_shot['label'].split('_')
    player = current_shot['player']
    shot = label_parts[2]
    specific_shot = label_parts[4]
    if specific_shot in ['lob', 'smash', 'volley']:
        shot = specific_shot
    court = label_parts[1][:2]  # e.g., 'de' or 'ad'
    side = label_parts[3] if shot != 'serve' else ''  # For serve, no side is needed       
    return player, shot, court, side

def parse_shot_data(json_file):
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Initialize a dictionary to hold shot type counts for each successor state
    shot_counts = defaultdict(lambda: defaultdict(int))

    # Loop through each match entry in the JSON file
    for rally in data:
        events = rally['events']
        service_player, shot, court, side = get_shot_fields(events[0])
        formation = "T%sC" % (1 if int(service_player[1]) <= 2 else 2)
        print(service_player, formation)
        # Iterate through events in pairs to capture shot type and its successor state
        for i in range(len(events)):
            current_shot = events[i]
            # Extract player, court, shot type, and outcome from the current shot
            player, shot, court, side = get_shot_fields(current_shot)
            
            # Create the shot type key
            if shot == 'serve':
                shot_type = f"{player}_{court.capitalize()}Serve"
            elif shot == 'secondserve':
                shot_type = f"{player}_{court.capitalize()}Secondserve"
            else:
                shot_type = f"{player}_{court.capitalize()}{shot.capitalize()}_{side.upper()}"
            if i + 1 < len(events):
                next_shot = events[i + 1]
            # Get the outcome/next state of the shot (e.g., P3_DeReturn_BH, Error, Ace, etc.)
            if current_shot['outcome'] == 'err':
                next_state = 'Error'
            elif current_shot['outcome'] == 'win':
                next_state = 'Win'
            else:
                next_player, next_shot_type, next_court, next_side = get_shot_fields(next_shot)
                if 'serve' in next_shot_type:
                    next_state = f"{next_player}_{next_court.capitalize()}{next_shot_type.capitalize()}"
                else:
                    next_state = f"{next_player}_{next_court.capitalize()}{next_shot_type.capitalize()}_{next_side.upper()}"
            # shot_type += ("_%s" % (formation))
            # next_state += ("_%s" % (formation))
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
    import time
    time.sleep(5)
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
        is_first_serve = "Serve" in key
        is_second_serve = "Secondserve" in key
        output += "%s = %sReady -> pcase { \n" % (key, key) 
        
        # Sort the inner dictionary by value (count) in descending order
        sorted_actions = sorted(value.items(), key=lambda x: x[1], reverse=True)
        
        for action, count in sorted_actions:
            if 'Error' in action:
                if is_first_serve:
                    new_key = key.replace("Serve", "Secondserve")
                    output += f"\t{count}: {new_key}\n"
                else:
                    output += f"\t{count}: {key}_err -> Error{{call(awardPoint, {player}, true)}} -> NextPt\n" 
            elif 'Win' in action:
                output += f"\t{count}: {key}_win -> Winner{{call(awardPoint, {player}, false)}} -> NextPt\n"
            else:
                output += f"\t{count}: {action}\n"
        
        output += "};\n"
    assertions = '''#define Team1Win won==t1;\n#define Team2Win won==t2;\n#assert TieBreakGame reaches Team1Win with prob;\n#assert TieBreakGame reaches Team2Win with prob;'''
    output += assertions
    output_filename = 'tennis_pcase_output.pcsp'
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
    print(full_data)
    print(eval_pcsp(generate_pcsp(full_data)))
