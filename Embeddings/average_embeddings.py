import pandas as pd

# Read the two CSV files into separate dataframes
file1 = "Image/vit-botw.csv"
file2 = "Image/vit-cub-200.csv"

drop_column = 'species'

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

species = df1[drop_column]

df1 = df1.drop(columns=[drop_column])
df2 = df2.drop(columns=[drop_column])

combined_df = (df1 + df2) / 2

combined_df.insert(0, 'species', species)
# Store the combined dataframe to a new CSV file
combined_df.to_csv("Image/combined_data.csv", index=False)
