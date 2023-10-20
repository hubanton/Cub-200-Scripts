import pandas as pd

# Read the two CSV files into separate dataframes
file1 = "Audio/ast-embeddings-botw.csv"
file2 = "Audio/ast-embeddings-xeno-canto.csv"
df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# Print the number of rows in the individual dataframes
print(f"Number of rows in {file1}: {len(df1)}")
print(f"Number of rows in {file2}: {len(df2)}")

# Combine the dataframes
combined_df = pd.concat([df1, df2], ignore_index=True)

# Both embeddings contain the Phoebetria_fusca recordings fetched from facebook and thus need to be removed
combined_df = combined_df.drop_duplicates()

# Print the number of rows in the combined dataframe
print(f"Number of rows in the combined dataframe: {len(combined_df)}")

# Perform additional data cleaning or manipulation here if needed

# Store the combined dataframe to a new CSV file
combined_df.to_csv("Audio/combined_data.csv", index=False)
