try:
    import tensorflow as tf
    import pandas as pd
    import numpy as np
except ImportError as e:
    raise Exception('Unable to import TensorFlow/pandas/numpy, make sure you have them installed')

from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, CSVLogger

import os
from argparse import ArgumentParser, Namespace, ArgumentTypeError
from datetime import datetime
from typing import Iterator, Tuple


MODEL_DIR = 'models'


def build_model(name: str) -> Sequential:
    """Create a new model with fully-connected layers
    where the input layer accepts 5 inputs:
    `id_map`, `start_x`, `start_y`, `target_x` and `target_y`
    and outputs predictions for `path_cost`
    """
    model = Sequential(name=name)
    model.add(Input(shape=(5,), name='input_layer'))

    model.add(Dense(units=400, activation='relu', kernel_initializer='he_normal', name='hidden_1'))
    model.add(Dense(units=500, activation='relu', kernel_initializer='he_normal', name='hidden_2'))
    model.add(Dense(units=400, activation='relu', kernel_initializer='he_normal', name='hidden_3'))

    model.add(Dense(units=1, activation='linear', name='output_layer'))
    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='mean_squared_error',
        metrics=['mean_squared_error']
    )
    return model


def _load_model(model_path: str) -> Sequential:
    """Load existing model.
    Avoid TF version issues when loading model by compiling it separately
    e.g. model_path = 'anya_dnn/20230627_193056/final_model.h5'
         full_model_path = '<MODEL_DIR>/anya_dnn/20230627_193056/final_model.h5'
    """
    try:
        full_model_path = os.path.join(MODEL_DIR, model_path)
        
        model = load_model(full_model_path, compile=False)
        model.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='mean_squared_error',
            metrics=['mean_squared_error']
        )
        return model
    except Exception as e:
        raise Exception(f'Could not load model: {e}')


def train_model(
    model: Sequential,
    batch_size: int,
    epochs: int,
    patience: int,
    training_generator: Iterator[Tuple[np.ndarray, np.ndarray]],
    dataset_size: int,
    verbose: int
) -> None:
    """Train a given model during N epochs, sending X batches.
    Save the model on every epoch end with a ModelCheckpoint instance.
    In case the model does not progress after certain period of training,
    EarlyStopping is used to stop the training process after N epochs (patience).
    CSVLogger keeps track of epoch training.
    verbose 1 means progress bar for each epoch whereas 0 is silent
    """
    model_path = create_folder(model.name)

    filepath = os.path.join(model_path, 'saved-model-{epoch:02d}-{loss:.4f}.hdf5')
    checkpoint = ModelCheckpoint(
        filepath=filepath,
        monitor='mean_squared_error',
        verbose=verbose,
        save_best_only=True,
        mode='auto'
    )

    early_stop = EarlyStopping(
        monitor='mean_squared_error',
        patience=patience,
        verbose=verbose,
        restore_best_weights=True
    )

    csv_logger = CSVLogger(os.path.join(model_path, 'training.log'), append=True)

    history = model.fit(
        training_generator,
        batch_size=batch_size,
        epochs=epochs,
        callbacks=[checkpoint, early_stop, csv_logger],
        steps_per_epoch=(dataset_size // batch_size),
        verbose=verbose
    )

    model.save(os.path.join(model_path, 'final_model.h5'))
    model.save_weights(os.path.join(model_path, 'final_w_model.hdf5'))


def create_folder(model_name: str) -> str:
    """Models are structured in folders and sub-folders.
    A model can be trained multiple times at different times.
    
    The folders structure is as follow:
    <MODEL_DIR> is the root folder and its sub-folders are the models.
    A model folder has versions of that model which ran at specific times
    those representing sub-folders with trained model file and checkpoints.
    An example of valid structure: <MODEL_DIR>/anya_dnn/20230628_130538/final_model.h5
    """
    model_path = f'{MODEL_DIR}/{model_name}'
    this_model_path = os.path.join(model_path, f'{datetime.now():%Y%m%d_%H%M%S}')
    
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    os.mkdir(this_model_path)
    return this_model_path


def dataset_generator(
    filename: str,
    batch_size: int,
    dataset_size: int,
    n_entries: int = 5
) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    """Read CSV file in chunks while dropping unnecessary columns and
    preparing each chunk to be consumed by the DNN.
    Each chunk represents a batch for the DNN
    """
    while True:
        reader = pd.read_csv(
            filename,
            sep=';',
            usecols=['id_map', 'start', 'target', 'path_cost'],
            converters={'path_cost': np.float64},
            chunksize=batch_size,
            nrows=dataset_size
        )
        for chunk in reader:
            chunk = apply_conversions(chunk.copy())
            w = chunk.values
            x = w[:, :n_entries]
            y = w[:, n_entries]
            yield x, y


def apply_conversions(df: pd.DataFrame) -> pd.DataFrame:
    """Split `start` and `target` coordinate tuples into separate columns
    and convert map name to float.
    Return Dataframe with columns reordered where last column is the DNN output target

    Examples
    -------
    Converting column of start coordinates tuple strings to start_x and start_y float columns
    >>> df = pd.DataFrame(['(123, 44)', '(92, 87)'], columns=['start'])
    >>> df
        start
    0  (123, 44)
    1   (92, 87)
    >>> df[['start_x', 'start_y']] = df.pop('start').str.strip('()').str.split(', ', n=1, expand=True).astype(float)
    >>> df
        start_x  start_y
    0    123.0     44.0
    1     92.0     87.0

    Converting map name to float character by character using ASCII table
    >>> df = pd.DataFrame(['London_0_512', 'Boston_1_1024'], columns=['id_map'])
    >>> df
                   id_map
    0       London_0_512
    1      Boston_1_1024
    >>> df['id_map'] = df['id_map'].apply(lambda row: convert_s2f(row)).astype(np.float64)
    >>> df
        id_map
    0  1008.0
    1  1067.0

    """

    df[['start_x', 'start_y']] = df.pop('start').str.strip('()').str.split(', ', n=1, expand=True).astype(np.float64)
    df[['target_x', 'target_y']] = df.pop('target').str.strip('()').str.split(', ', n=1, expand=True).astype(np.float64)
    df['id_map'] = df['id_map'].apply(lambda row: convert_s2f(row)).astype(np.float64)

    return df[['id_map', 'start_x', 'start_y', 'target_x', 'target_y', 'path_cost']]


def convert_s2f(value: str) -> float:
  """Convert string to float character by character"""
  return sum([ord(char) for char in value])


def parser() -> Namespace:
    def restricted_float(x: str) -> float:
        try:
            x = float(x)
        except ValueError as e:
            raise ArgumentTypeError(f'Expecting argument type "float", got: "{type(x).__name__}"')
        if x == 0.0:
            raise ArgumentTypeError('Dataset size of 0.0 is not allowed') 
        elif x < 0.0 or x > 1.0:
            raise ArgumentTypeError(f'Value not in range [0.0, 1.0]: {x}')
        return x

    parser = ArgumentParser()
    parser.add_argument('-mode', '--mode',
                        type=lambda arg: arg.lower(),
                        choices=['create', 'load'],
                        required=True,
                        help='Create a new model or load existing model (case-insensitive)')

    parser.add_argument('-f_path', '--file_path',
                        required=True,
                        help='Path for the training dataset')

    parser.add_argument('-d_size', '--dataset_size',
                        nargs='?',
                        default=1.0,
                        type=restricted_float,
                        help=('Size of training dataset to be used. '
                              'Ranges from 0 - 1 (0%% and 100%% respectively). Defaults to whole dataset'))

    parser.add_argument('-m_path', '--model_path',
                        help='Path for existing model. Required in "load" mode')

    parser.add_argument('-m_name', '--model_name',
                        help='Meaningful name for the new model. Required in "create" mode')

    parser.add_argument('-v', '--verbose', action='store_false',
                        help='Verbose training. Defaults to True if not specified')
    
    args = parser.parse_args()

    if args.mode == 'load' and args.model_path is None:
        parser.error('Load mode requires -m_path/--model_path')
    elif args.mode == 'create' and args.model_name is None:
        parser.error('Create mode requires -m_name/--model_name')
    return args


def get_dataset_size(file_path: str) -> int:
    """Open dataset file and count number of rows for the training session.
    NOTE: need to take into account that the file has header, so "- 1"
    """
    try:
        file = open(file_path)
        dataset_size = len(file.readlines()) - 1
        file.close()
        return dataset_size
    except Exception as e:
        raise Exception(f'Error reading dataset: {e}')


def main():
    args = parser()

    if args.mode == 'create':
        model = build_model(args.model_name)
    elif args.mode == 'load':
        model = _load_model(args.model_path)

    orig_dataset_size = get_dataset_size(args.file_path)
    if orig_dataset_size <= 0:
        raise Exception(f'Dataset provided has {orig_dataset_size} lines')

    batch_size = 32
    dataset_size = int(orig_dataset_size * args.dataset_size)
    training_generator = dataset_generator(args.file_path, batch_size, dataset_size)

    train_model(
        model,
        batch_size,
        epochs=100,
        patience=30,
        training_generator=training_generator,
        dataset_size=dataset_size,
        verbose=1 if args.verbose else 0
    )


if __name__ == '__main__':
    main()
