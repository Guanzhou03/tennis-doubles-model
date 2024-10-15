import argparse
import json
from collections import defaultdict
import os
import re

def get_undefined_serves(serves):
    output = '\n'
    for player in range(1, 5):
        # Check and assign DeServe_PxC
        if f"P{player}_DeServe_P{player}C" not in serves:
            output += f"P{player}_DeServe_P{player}C = P{player}_DeServe_P{player}I;\n"
        
        # Check and assign AdServe_PxC
        if f"P{player}_AdServe_P{player}C" not in serves:
            output += f"P{player}_AdServe_P{player}C = P{player}_AdServe_P{player}I;\n"
        
        # Check and assign DeServe_PxI
        if f"P{player}_DeServe_P{player}I" not in serves:
            output += f"P{player}_DeServe_P{player}I = P{player}_DeServe_P{player}C;\n"
        
        # Check and assign AdServe_PxI
        if f"P{player}_AdServe_P{player}I" not in serves:
            output += f"P{player}_AdServe_P{player}I = P{player}_AdServe_P{player}C;\n"
    
    return output
            
def update_formation_text_in_file(file_path, formation_counts):
    # Read the content of the file
    with open(file_path, 'r') as file:
        text = file.read()
    
    text = re.sub(r'\d+: C_Formation\{p1_form=C\}', f"{formation_counts['P1C']}: C_Formation{{p1_form=C}}", text)
    text = re.sub(r'\d+: I_Formation\{p1_form=I\}', f"{formation_counts['P1I']}: I_Formation{{p1_form=I}}", text)
    
    text = re.sub(r'\d+: C_Formation\{p2_form=C\}', f"{formation_counts['P2C']}: C_Formation{{p2_form=C}}", text)
    text = re.sub(r'\d+: I_Formation\{p2_form=I\}', f"{formation_counts['P2I']}: I_Formation{{p2_form=I}}", text)
    
    text = re.sub(r'\d+: C_Formation\{p3_form=C\}', f"{formation_counts['P3C']}: C_Formation{{p3_form=C}}", text)
    text = re.sub(r'\d+: I_Formation\{p3_form=I\}', f"{formation_counts['P3I']}: I_Formation{{p3_form=I}}", text)
    
    text = re.sub(r'\d+: C_Formation\{p4_form=C\}', f"{formation_counts['P4C']}: C_Formation{{p4_form=C}}", text)
    text = re.sub(r'\d+: I_Formation\{p4_form=I\}', f"{formation_counts['P4I']}: I_Formation{{p4_form=I}}", text)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(text)
        
def get_shot_fields(current_shot):
    # maps the data given to their corresponding indices after splitting with _ 
    data_indices = {"player_idx": 0, "court_idx": 2, "handedness_idx": 3, "shot_idx": 4, "shot_direction_idx": 5, "formation_idx":6, "outcome_idx": -1}
    label_parts = current_shot['event'].split('_')
    isFH = "forehand" in label_parts[data_indices["handedness_idx"]]
    player = label_parts[data_indices["player_idx"]]
    shot = label_parts[data_indices["shot_idx"]].replace('-', '').capitalize()
    court = label_parts[data_indices["court_idx"]][:2].capitalize()  # e.g., 'de' or 'ad'
    outcome = label_parts[data_indices["outcome_idx"]]
    formation = label_parts[data_indices["formation_idx"]]
    service_formation = None
    if 'serve' not in shot.lower():
        side = "FH" if isFH else "BH"
    else:
        side = ''
        if "conventional" in formation:
            service_formation = "%sC" % (player)
            serves.add("_".join([player, court+shot, player + "C"]))
        elif "i-formation" in formation:
            service_formation = "%sI" % (player)
            serves.add("_".join([player, court+shot, player + "I"]))
        formation_counts[service_formation] += 1
    return player, shot, court, side, outcome, service_formation

def parse_shot_data(json_file):
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Dict to hold shot type counts for each successor state
    shot_counts = defaultdict(lambda: defaultdict(int))
   
    # Loop through each match entry in the JSON file
    for rally in data['rallies']:
        events = rally['events']

        # Iterate through events in pairs to capture shot type and its successor state
        for i in range(len(events)):
            current_shot = events[i]
            # Extract player, court, shot type, and outcome from the current shot
            player, shot, court, side, outcome, service_formation = get_shot_fields(current_shot)
            if service_formation:
                # current shot is a serve
                formation = service_formation
            # Create the shot type key
            if 'serve' in shot.lower():
                shot_type = f"{player}_{court}{shot}"
            else:
                shot_type = f"{player}_{court}{shot}_{side}"
            if i + 1 < len(events):
                next_shot = events[i + 1]
            
            if outcome == 'err' and shot != 'Serve':
                # not first service, and err
                next_state = 'Error'
            elif outcome == 'win':
                next_state = 'Win'
            else:
                # not err or win, have next state
                next_player, next_shot_type, next_court, next_side, _, next_formation = get_shot_fields(next_shot)
                if 'serve' in next_shot_type.lower():
                    # second serve
                    next_state = f"{next_player}_{next_court}{next_shot_type}"
                    next_state += ("_%s" % (next_formation)) 
                else:
                    next_state = f"{next_player}_{next_court}{next_shot_type}_{next_side}"
                    next_state += ("_%s" % (formation)) 
            shot_type += ("_%s" % (formation))
            # Increment the count for this shot type and successor state
            shot_counts[shot_type][next_state] += 1
    update_formation_text_in_file("env_with_formation.pcsp", formation_counts)
    # print(formation_counts)
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


def generate_pcsp(counts_dict, to_add):
    output = '#include "formation_env.pcsp";\n'
    for key, value in counts_dict.items():
        player = key[1]
        output += "%s = %sReady -> pcase { \n" % (key, key) 
        
        # Sort the inner dictionary by value (count) in descending order
        sorted_successors = sorted(value.items(), key=lambda x: x[1], reverse=True)
        for successor, count in sorted_successors:
            if 'Error' in successor:
                output += f"\t{count}: {key}_err -> Error{{call(awardPoint, {player}, true)}} -> NextPt\n" 
            elif 'Win' in successor:
                output += f"\t{count}: {key}_win -> Winner{{call(awardPoint, {player}, false)}} -> NextPt\n"
            else:
                output += f"\t{count}: {successor}\n"
        
        output += "};\n"
    assertions = '''#define Team1Win won==t1;\n#define Team2Win won==t2;\n#assert TieBreakGame reaches Team1Win with prob;\n#assert TieBreakGame reaches Team2Win with prob;'''
    output += assertions
    output += to_add
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
    serves = set()
     # Counts to update formation
    formation_counts = {"P1C":0, "P1I":0, "P2C":0, "P2I":0, "P3C":0, "P3I":0, "P4C":0, "P4I":0}
    for json_file in args.json:
        shot_data = parse_shot_data(json_file)
        full_data = merge_dicts(full_data, shot_data)
    # print(full_data)
    print(eval_pcsp(generate_pcsp(full_data, get_undefined_serves(serves))))
