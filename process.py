import json
import requests
import random
import os
from datetime import datetime

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def select_words(words, used_words, count=3):
    selected_words = []
    while len(selected_words) < count:
        word = random.choice(words)
        if word not in used_words and word not in selected_words:
            selected_words.append(word)
    return selected_words

def clean_entry(entry):
    keys_to_remove = {'sourceUrls', 'license', 'audio', 'sourceUrl'}
    
    def recursive_clean(data):
        if isinstance(data, dict):
            return {k: recursive_clean(v) for k, v in data.items() if k not in keys_to_remove}
        elif isinstance(data, list):
            return [recursive_clean(item) for item in data]
        else:
            return data
    
    return recursive_clean(entry)

# Load words from words.json
words = load_json_file('words.json')

# Load used words from used.json
used_words = load_json_file('used.json')

# Ensure words list is not empty
if not words:
    print("The words.json file is empty or not a valid JSON.")
    exit()

# Select 3 words
selected_words = select_words(words, used_words)

# Fetch definitions from the API
api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
definitions = []

for word in selected_words:
    response = requests.get(f"{api_url}{word}")
    if response.status_code == 200:
        cleaned_definition = clean_entry(response.json())
        definitions.append(cleaned_definition)
    else:
        print(f"Failed to fetch definition for {word}")

# Save the definitions to today.json
with open('today.json', 'w') as file:
    json.dump(definitions, file, indent=4)

# Get the current date in the format YYYY-MM-DD
current_date = datetime.now().strftime('%Y-%m-%d')

# Create archive folder if it does not exist
archive_folder = 'archive'
if not os.path.exists(archive_folder):
    os.makedirs(archive_folder)

# Save the definitions to a file in the archive folder named with today's date
archive_file_path = os.path.join(archive_folder, f'{current_date}.json')
with open(archive_file_path, 'w') as file:
    json.dump(definitions, file, indent=4)

# Add selected words to used.json
used_words.extend(selected_words)
with open('used.json', 'w') as file:
    json.dump(used_words, file, indent=4)

# Print the selected words
print(f"Selected words: {selected_words}")
