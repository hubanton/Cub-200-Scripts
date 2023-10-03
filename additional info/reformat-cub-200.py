# Define the input file path
input_file_path = "cub-200-folder-names.txt"

# Read the content of the input file and remove the first number from each line
with open(input_file_path, "r") as file:
    lines = file.readlines()

modified_lines = [line.split(maxsplit=1)[1] for line in lines]

# Overwrite the input file with the modified content
with open(input_file_path, "w") as file:
    file.writelines(modified_lines)

print("File successfully modified and overwritten.")