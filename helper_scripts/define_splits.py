import os
import random

import pandas as pd

file_path = "../Embeddings/Audio/ast-embeddings-botw.csv"

df = pd.read_csv(file_path)

df['species'] = df['filename'].apply(lambda x: x.split('/')[0])

class_list = list(df['species'].unique())

# Define the number of splits
num_splits = 5

# Define the split ratios
train_ratio = 0.75
dev_ratio = 0.125
test_ratio = 0.125

ROOT_FOLDER = 'folds'
os.makedirs(ROOT_FOLDER, exist_ok=True)

splits = []

for i in range(num_splits):
    random.shuffle(class_list)

    print(f"Fold {i + 1}:")
    child_folder = os.path.join(ROOT_FOLDER, str(i + 1))
    os.makedirs(child_folder, exist_ok=True)

    total_len = len(class_list)

    train_len = int(total_len * train_ratio)
    test_len = int(total_len * test_ratio)
    dev_len = int(total_len * dev_ratio)

    # Fetch train_len random classes from entire list
    train_classes = class_list[:train_len]

    print(len(train_classes))
    # Get remaining classes
    test_dev_list = [c for c in class_list if c not in train_classes]

    print(test_dev_list)
    # Get all classes not previously used for the test set
    test_list = test_dev_list.copy()
    if len(splits) != 0:
        for split in splits:
            test_list = [c for c in test_list if c not in split[2]]

    test_classes = test_list[:test_len]

    dev_list = test_dev_list.copy()
    dev_list = [c for c in dev_list if c not in test_classes]
    if len(splits) != 0:
        for split in splits:
            dev_list = [c for c in dev_list if c not in split[1]]

    dev_classes = dev_list[:dev_len]

    splits.append((train_classes, dev_classes, test_classes))

    TARGET_COLUMN = ['species']
    df_train = pd.DataFrame(train_classes, columns=TARGET_COLUMN)
    df_test = pd.DataFrame(test_classes, columns=TARGET_COLUMN)
    df_dev = pd.DataFrame(dev_classes, columns=TARGET_COLUMN)

    df_train.to_csv(os.path.join(child_folder, 'train.csv'), index=False)
    df_test.to_csv(os.path.join(child_folder, 'test.csv'), index=False)
    df_dev.to_csv(os.path.join(child_folder, 'dev.csv'), index=False)
