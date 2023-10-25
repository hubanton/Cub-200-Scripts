import os
import re

# Define the input and output folders
input_folder = 'Text'
output_folder = 'Text_filtered'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

removable_strings = ['Sounds and Vocal Behavior', 'Macaulay Library', 'See above.', 'audio', 'audio.', 'audio,', 'seek',
                     'mute', 'See text for details...']

# Loop through all .txt files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        # Read the contents of the input file
        with open(os.path.join(input_folder, filename), 'r') as file:
            text = file.read()

        # Remove references to recordings or figures
        matches = text.split('.')
        for match in matches:
            if 'recorded in' in match or 'In order,' in match or 'Figure' in match:
                text = text.replace(match, '')

        # Remove all media references
        filtered_text = re.sub(r"Macaulay Library ML \d+", '', text)
        filtered_text = re.sub(r"ML\d+", '', filtered_text)
        filtered_text = re.sub(r"ML \d+", '', filtered_text)
        filtered_text = re.sub(r'[\w\s]+,\s[\w\s]+,\s[\w\s]+ \d{1,2} \w{3} \d{4}', '', filtered_text)
        filtered_text = re.sub(r"([\w\s]+),\s([\w\s]+),\s(\d{1,2}\s\w+\s\d{4})", '', filtered_text)
        filtered_text = re.sub(r"\d{1,2}\s\w+\s\d{4}", '', filtered_text)
        filtered_text = re.sub(r'\d+:\d+', '', filtered_text)
        filtered_text = re.sub(r'Figure \d+[A-Za-z]: .*', '', filtered_text, flags=re.MULTILINE)
        filtered_text = re.sub(r'Video: .*', '', filtered_text, flags=re.MULTILINE)
        filtered_text = re.sub(r'Video: .*', '', filtered_text, flags=re.MULTILINE)
        filtered_text = re.sub(r'recorded in \d{4} in [^,.]+[,.]', '', filtered_text, flags=re.MULTILINE)
        filtered_text = re.sub(r'\s+', ' ', filtered_text, flags=re.MULTILINE)

        # Remove content inside brackets
        filtered_text = re.sub(r'\[[^\]]*\]', '', filtered_text)
        # Remove content inside parenthesis
        filtered_text = re.sub(r'\([^)]*\)', '', filtered_text)

        # Remove sentences matching the pattern "Figure <number>."
        filtered_text = re.sub(r'Figure \d+\.', '', filtered_text)

        # Remove unwanted strings
        for unwanted_string in removable_strings:
            filtered_text = filtered_text.replace(unwanted_string, "")

        # Remove leading white-spaces before comma, period, and colon
        filtered_text = re.sub(r'\s+([,.:;])(?!\S)', r'\1', filtered_text)

        # Remove copyright lines
        lines = filtered_text.split('\n')
        stripped_lines = ['' if line.startswith("© ") else line for line in lines]
        filtered_text = '\n'.join(stripped_lines)

        # Remove whitespaces
        lines = filtered_text.splitlines()
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        filtered_text = '\n'.join(non_empty_lines)

        # Write the filtered text to the output file
        with open(os.path.join(output_folder, filename), 'w') as filtered_file:
            filtered_file.write(filtered_text)

print("Filtering completed. Filtered files are stored in the output folder.")
