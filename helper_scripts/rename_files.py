import os


def rename_files(folder_path, current_names, new_names, suffix):
    if len(current_names) != len(new_names):
        print("Error: The number of current and new item names must be the same.")
        return

    for i in range(len(current_names)):
        current_name = current_names[i] + suffix
        new_name = new_names[i]

        current_path = os.path.join(folder_path, current_name)
        new_path = os.path.join(folder_path, new_name)

        if os.path.exists(current_path):
            os.rename(current_path, new_path)
            print(f"Renamed '{current_name}' to '{new_name}'")
        else:
            print(f"File '{current_name}' not found in the folder.")


with open('../shared/en_names.txt', 'r') as f:
    current_names = f.read().splitlines()

with open('../shared/latin_names.txt', 'r') as f:
    new_names = f.read().splitlines()

rename_files('../xeno_canto_data/Recordings', current_names, new_names, '')
