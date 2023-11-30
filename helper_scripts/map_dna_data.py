import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('../Embeddings/DNA/cub_dna_embeddings.csv')

# Load the original names
with open('../shared/dna_names.txt', 'r') as file:
    og_names = file.read().splitlines()


# Function to preprocess the names
def preprocess_name(name):
    # Remove '#' and everything that comes after it
    name = name.split('#')[0]
    # Replace underscores with spaces and convert to lowercase
    return name.replace('_', ' ').strip()


# Preprocess the original names
og_names = [preprocess_name(name) for name in og_names]

# Load the new names
with open('../shared/latin_names.txt', 'r') as file:
    new_names = file.read().splitlines()

species_list = df['species'].tolist()

for i in range(len(og_names)):
    species_list = [new_names[i] if item == og_names[i] else item for item in species_list]

df['species'] = species_list

# Save the updated DataFrame to a new CSV file
df.to_csv('../Embeddings/DNA/cub_dna_embeddings_MAPPED_NAMES.csv', index=False)

new_list = set(df['species'].tolist())

print('Birds with no recordings', set(new_names) - set(new_list))
print('Birds that were not correctly mapped', set(new_list) - set(new_names))

# Print a message indicating the save was successful
print("Mapped names saved to cub_dna_embeddings_MAPPED_NAMES.csv")
