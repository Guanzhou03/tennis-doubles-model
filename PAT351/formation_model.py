import argparse
import json
from collections import defaultdict
import os
import re

class FormationModel:
    def __init__(self):
        # Initialize the counts dictionary and other necessary attributes
        self.counts_dict = {}
        self.serves = set()
        self.formation_counts = {
            "P1C": 0, "P1I": 0,
            "P2C": 0, "P2I": 0,
            "P3C": 0, "P3I": 0,
            "P4C": 0, "P4I": 0
        }

    def get_undefined_serves(self):
        output = '\n'
        for player in range(1, 5):
            # Check and assign DeServe_PxC
            if f"P{player}_DeServe_P{player}C" not in self.serves:
                output += f"P{player}_DeServe_P{player}C = P{player}_DeServe_P{player}I;\n"

            # Check and assign AdServe_PxC
            if f"P{player}_AdServe_P{player}C" not in self.serves:
                output += f"P{player}_AdServe_P{player}C = P{player}_AdServe_P{player}I;\n"

            # Check and assign DeServe_PxI
            if f"P{player}_DeServe_P{player}I" not in self.serves:
                output += f"P{player}_DeServe_P{player}I = P{player}_DeServe_P{player}C;\n"

            # Check and assign AdServe_PxI
            if f"P{player}_AdServe_P{player}I" not in self.serves:
                output += f"P{player}_AdServe_P{player}I = P{player}_AdServe_P{player}C;\n"

        return output

    def update_formation_text_in_file(self, file_path):
        # Read the content of the file
        with open(file_path, 'r') as file:
            text = file.read()

        text = re.sub(r'\d+: C_Formation\{p1_form=C\}', f"{self.formation_counts['P1C']}: C_Formation{{p1_form=C}}", text)
        text = re.sub(r'\d+: I_Formation\{p1_form=I\}', f"{self.formation_counts['P1I']}: I_Formation{{p1_form=I}}", text)

        text = re.sub(r'\d+: C_Formation\{p2_form=C\}', f"{self.formation_counts['P2C']}: C_Formation{{p2_form=C}}", text)
        text = re.sub(r'\d+: I_Formation\{p2_form=I\}', f"{self.formation_counts['P2I']}: I_Formation{{p2_form=I}}", text)

        text = re.sub(r'\d+: C_Formation\{p3_form=C\}', f"{self.formation_counts['P3C']}: C_Formation{{p3_form=C}}", text)
        text = re.sub(r'\d+: I_Formation\{p3_form=I\}', f"{self.formation_counts['P3I']}: I_Formation{{p3_form=I}}", text)

        text = re.sub(r'\d+: C_Formation\{p4_form=C\}', f"{self.formation_counts['P4C']}: C_Formation{{p4_form=C}}", text)
        text = re.sub(r'\d+: I_Formation\{p4_form=I\}', f"{self.formation_counts['P4I']}: I_Formation{{p4_form=I}}", text)

        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.write(text)

    def get_shot_fields(self, current_shot):
        # Map the data given to their corresponding indices after splitting with '_'
        data_indices = {
            "player_idx": 0,
            "court_idx": 2,
            "handedness_idx": 3,
            "shot_idx": 4,
            "shot_direction_idx": 5,
            "formation_idx": 6,
            "outcome_idx": -1
        }
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
                service_formation = f"{player}C"
                self.serves.add("_".join([player, court + shot, player + "C"]))
            elif "i-formation" in formation:
                service_formation = f"{player}I"
                self.serves.add("_".join([player, court + shot, player + "I"]))
            self.formation_counts[service_formation] += 1
        return player, shot, court, side, outcome, service_formation

    def parse_shot_data(self, json_file):
        # Load JSON data
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Dict to hold shot type counts for each successor state
        shot_counts = defaultdict(lambda: defaultdict(int))

        # Loop through each rally in the JSON file
        for rally in data['rallies']:
            events = rally['events']

            # Iterate through events to capture shot type and its successor state
            for i in range(len(events)):
                current_shot = events[i]
                # Extract player, court, shot type, and outcome from the current shot
                player, shot, court, side, outcome, service_formation = self.get_shot_fields(current_shot)
                if service_formation:
                    # Current shot is a serve
                    formation = service_formation
                # Create the shot type key
                if 'serve' in shot.lower():
                    shot_type = f"{player}_{court}{shot}"
                else:
                    shot_type = f"{player}_{court}{shot}_{side}"
                if i + 1 < len(events):
                    next_shot = events[i + 1]

                if outcome == 'err' and shot != 'Serve':
                    # Not first service and error
                    next_state = 'Error'
                elif outcome == 'win':
                    next_state = 'Win'
                else:
                    # Not error or win, have next state
                    next_player, next_shot_type, next_court, next_side, _, next_formation = self.get_shot_fields(next_shot)
                    if 'serve' in next_shot_type.lower():
                        # Second serve
                        next_state = f"{next_player}_{next_court}{next_shot_type}_{next_formation}"
                    else:
                        next_state = f"{next_player}_{next_court}{next_shot_type}_{next_side}_{formation}"
                shot_type += f"_{formation}"
                # Increment the count for this shot type and successor state
                shot_counts[shot_type][next_state] += 1


        # Merge the new counts into the main counts dictionary
        self.counts_dict = self.merge_dicts(self.counts_dict, shot_counts)

    def merge_dicts(self, dict1, dict2):
        # Merge dict2 into dict1 recursively
        for key, value in dict2.items():
            if key in dict1:
                # If the value is a dictionary, we recursively combine
                if isinstance(value, dict):
                    dict1[key] = self.merge_dicts(dict1[key], value)
                else:
                    # If value is an integer count, we add the counts
                    dict1[key] += value
            else:
                dict1[key] = value
        return dict1

    def eval_pcsp(self, file_name):
        # Evaluate the PCSP file using PAT3 console
        os.system(f'mono PAT3.Console.exe -pcsp {file_name} {file_name[:-5]}.txt')
        with open(f'{file_name[:-5]}.txt', 'r') as f:
            lines = f.readlines()
        if "VALID" in lines[3]:
            return 1
        elif "NOT valid" in lines[3]:
            return 0
        elif len(lines) < 5 or '[' not in lines[3] or ']' not in lines[3]:
            print(lines)
            return -1, -1
        # print(lines[3])
        min_max_probs = [float(score) for score in lines[3].split('[')[1].split(']')[0].split(',')]
        return (min_max_probs[0] + min_max_probs[1]) / 2

    def generate_pcsp(self, env_file):
        # Update formation text in the file
        self.update_formation_text_in_file(env_file[1:-1])
        output = f'#include {env_file};\n'
        sorted_keys = sorted(self.counts_dict)
        for key in sorted_keys:
            value = self.counts_dict[key]
            player = key[1]
            output += f"{key} = {key}Ready -> pcase {{\n"

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
        output += self.get_undefined_serves()
        output_filename = 'tennis_pcase_output.pcsp'
        with open(output_filename, 'w') as f:
            f.write(output)
        return output_filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', type=str, nargs='+', help="JSON file names")
    args = parser.parse_args()

    # Instantiate the Model
    model = FormationModel()

    # Process each JSON file
    for json_file in args.json:
        model.parse_shot_data(json_file)

    # Generate the PCSP file and evaluate it
    pcsp_file = model.generate_pcsp('"formation_env.pcsp"')
    print("Team 1 winning chance: ", model.eval_pcsp(pcsp_file))
