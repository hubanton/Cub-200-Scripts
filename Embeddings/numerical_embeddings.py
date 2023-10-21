import os
from sklearn.preprocessing import LabelEncoder
import audiofile
import pandas as pd
import torch
import transformers
from tqdm import tqdm
from transformers import AutoModelForAudioClassification, ASTFeatureExtractor

latin_names_file = '../shared/latin_names.txt'

filename = '../../audiocub-zsl/meta_information/avonet.xlsx'

target_directory = 'Numerical/avonet'


def readfile(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


def get_numeric_features(avo_file: str, latin_names):
    sheet_names = ['AVONET1_BirdLife', 'AVONET2_eBird', 'AVONET3_BirdTree']

    matching_rows = []
    already_added_names = []

    for index, sheet_name in enumerate(sheet_names):
        avo_df = pd.read_excel(avo_file, sheet_name=sheet_name)
        avo_df = avo_df.iloc[:, :-5]

        species_column_name = f'Species{index + 1}'
        species_column = avo_df[species_column_name].apply(lambda x: x.replace(' ', '_'))

        species_list = species_column.to_list()

        avo_df.drop(columns=[species_column_name])

        avo_df = avo_df.iloc[:, 10:]

        avo_df.insert(0, 'species', species_column)

        for latin_name in latin_names:
            if latin_name in species_list:
                if latin_name in already_added_names:
                    print(f'Bird already present {latin_name} {sheet_name}')
                else:
                    matching_rows.append(avo_df[avo_df['species'] == latin_name])
                    already_added_names.append(latin_name)


    raw_filtered_df = pd.concat(matching_rows, ignore_index=True)
    
    columns_with_nan = raw_filtered_df.columns[raw_filtered_df.isna().sum() >= 10].values.tolist()
    raw_filtered_df.drop(columns=columns_with_nan, inplace=True)

    for column in raw_filtered_df.iloc[:, 1:].select_dtypes(include='object'):
        raw_filtered_df[column] = LabelEncoder().fit_transform(raw_filtered_df[column].apply(str))

    final_df = raw_filtered_df.fillna(0)

    return final_df


latin_names = readfile(latin_names_file)

results = get_numeric_features(filename, latin_names)

results.to_csv(f'{target_directory}.csv', index=False)
