import pandas as pd
import numpy as np
import os
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

file_path = "../Embeddings/Audio/ast-embeddings-botw.csv"

df = pd.read_csv(file_path)

num_rows = len(df)

df['species'] = df['filename'].apply(lambda x: x.split('/')[0])

groups = df['species'].to_numpy()

X = np.ones((num_rows, 1))


sgkf = StratifiedGroupKFold(n_splits=5, random_state=42, shuffle=True)

ROOT_FOLDER = 'folds'
os.makedirs(ROOT_FOLDER, exist_ok=True)

for i, (train_index, test_index) in enumerate(sgkf.split(X, groups, groups)):
    print(f"Fold {i + 1}:")
    child_folder = os.path.join(ROOT_FOLDER, str(i + 1))
    os.makedirs(child_folder, exist_ok=True)

    train_classes = np.unique(groups[train_index])
    test_dev_classes = np.unique(groups[test_index])

    train_size = train_classes.shape[0]
    test_dev_size = test_dev_classes.shape[0]

    test_dev_split = test_dev_size // 2

    print('Ratio of train to test: ', test_dev_size / train_size)

    test_classes = test_dev_classes[:test_dev_split]
    dev_classes = test_dev_classes[test_dev_split:]

    TARGET_COLUMN = ['species']

    df_train = pd.DataFrame(train_classes, columns=TARGET_COLUMN)
    df_test = pd.DataFrame(train_classes, columns=TARGET_COLUMN)
    df_dev = pd.DataFrame(train_classes, columns=TARGET_COLUMN)

    df_train.to_csv(os.path.join(child_folder, 'train.csv'), index=False)
    df_test.to_csv(os.path.join(child_folder, 'test.csv'), index=False)
    df_dev.to_csv(os.path.join(child_folder, 'dev.csv'), index=False)