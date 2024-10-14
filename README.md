# Project Info
Tennis doubles modelling with automated parsing of tennis data in JSON, automated generation of PCSP code, and verification with PAT.

## Description

Able to take in tennis doubles data containing the shot events, in one or multiple JSON files. Parses input JSON and builds a PCSP file, which then executed using PAT console to obtain winning probability. 
Base model does not use formation data while formation model includes formation data.

## Executing program
Ensure Python is installed in your environment, and simply run the model in PAT351 folder.

To run the model:
```
python base_model.py -json <file_names>
python base_model.py -json VUPKfQgXy8g_transformed.json

python formation_model.py -json VUPKfQgXy8g_transformed.json
python formation_model.py -json *.json
```