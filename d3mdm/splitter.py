# -*- coding: utf-8 -*-

import json
import logging
import os
from collections import OrderedDict
from io import StringIO

import pandas as pd
from sklearn.model_selection import train_test_split

LOGGER = logging.getLogger(__name__)


def to_csv(df):
    buf = StringIO()
    df.to_csv(buf, index=None)
    return buf.getvalue().encode()


def read_csv(dataset, csv_path):
    data = dataset
    for level in csv_path.split('/'):
        data = data[level]

    return pd.read_csv(StringIO(data.decode()))


def write_csv(df, dataset, csv_path):
    folder = dataset
    levels = csv_path.split('/')
    for level in levels[:-1]:
        folder = folder[level]

    folder[levels[-1]] = to_csv(df)


def get_split(data_splits, learning_data, label):
    split_index = data_splits[data_splits['type'] == label].d3mIndex

    learning_data_indexed = learning_data.set_index('d3mIndex')

    split = learning_data_indexed.loc[split_index]
    return split.reset_index()


def get_problem_names(dataset, dataset_name):
    problem_names = []
    for key in dataset.keys():
        if dataset_name in key:
            key = key.replace(dataset_name, '').replace('_problem', '')
            if key != '_dataset':
                problem_names.append(key)

    return problem_names


def get_target_names(problem_data, learning_data, dataset_doc):
    target_names = [target['colName'] for target in problem_data['targets']]
    if all(target in learning_data for target in target_names):
        return target_names

    LOGGER.warning("Target names not found in learning data")
    LOGGER.warning("Falling back to using suggestedTarget roles")

    def learning_data_filter(d):
        return d['resPath'] == 'tables/learningData.csv'

    resources = dataset_doc['dataResources']
    learning_data_resource = list(filter(
        lambda d: d['resPath'] == 'tables/learningData.csv',
        resources
    ))[0]
    target_columns = filter(
        lambda d: 'suggestedTarget' in d['role'],
        learning_data_resource['columns']
    )

    return [column['colName'] for column in target_columns]


def build_data_splits(learning_data):
    train, test = train_test_split(learning_data, test_size=0.2, random_state=0)
    splits = pd.DataFrame(index=learning_data['d3mIndex'])
    splits.loc[train['d3mIndex'], 'type'] = 'TRAIN'
    splits.loc[test['d3mIndex'], 'type'] = 'TEST'
    splits['repeat'] = 0
    splits['fold'] = 0

    return splits.reset_index()


def get_data_splits(dataset, dataset_problem, learning_data):
    path = os.path.join(dataset_problem, 'dataSplits.csv')
    try:
        data_splits = read_csv(dataset, path)
    except Exception:
        LOGGER.warning('dataSplits.csv not found in %s. Generating one.', dataset_problem)
        data_splits = build_data_splits(learning_data)
        write_csv(data_splits, dataset, path)

    return data_splits


def get_dataset_split(full_dataset, dataset_name, label, problem, targets=False):
    problem_suffix = '_problem' + problem

    # get dataframes
    learning_data = read_csv(full_dataset, dataset_name + '_dataset/tables/learningData.csv')
    data_splits = get_data_splits(full_dataset, dataset_name + problem_suffix, learning_data)

    # get the learningData split
    learning_data_split = get_split(data_splits, learning_data, label)

    # NOTE: Here we use a copy instead of a deepcopy to avoid duplicating
    # all the data inside the tables structure
    # However, we still need to make the tables copy explicit to avoid
    # Overwritting the learningData.csv in the main dataset dict.
    dataset_split = full_dataset[dataset_name + '_dataset'].copy()
    dataset_split['tables'] = dataset_split['tables'].copy()

    suffix = '_' + label + problem

    # Prepare the datasetDoc.json
    dataset_doc = json.loads(dataset_split['datasetDoc.json'].decode(),
                             object_pairs_hook=OrderedDict)
    dataset_id = dataset_doc['about']['datasetID'] + suffix
    dataset_doc['about']['datasetID'] = dataset_id

    # preparo the problemDoc.json
    problem_split = full_dataset[dataset_name + problem_suffix].copy()
    problem_doc = json.loads(problem_split['problemDoc.json'].decode(),
                             object_pairs_hook=OrderedDict)

    problem_doc['about']['problemID'] += suffix
    problem_data = problem_doc['inputs']['data'][0]

    problem_data['datasetID'] = dataset_id

    target_names = get_target_names(problem_data, learning_data, dataset_doc)

    dataset_split['datasetDoc.json'] = json.dumps(dataset_doc, indent=2).encode()
    problem_split['problemDoc.json'] = json.dumps(problem_doc, indent=2).encode()

    split = {
        'problem_' + label: problem_split,
        'dataset_' + label: dataset_split
    }

    if targets:
        split['targets.csv'] = to_csv(learning_data_split[['d3mIndex'] + target_names])

    if label == 'TEST':
        for target_name in target_names:
            learning_data_split[target_name] = None

    dataset_split['tables']['learningData.csv'] = to_csv(learning_data_split)

    return split


def add_dataset_splits(dataset, dataset_name):
    LOGGER.info('Adding dataset splits to %s', dataset_name)
    problems = get_problem_names(dataset, dataset_name)
    for problem in problems:
        dataset['TRAIN' + problem] = get_dataset_split(
            dataset, dataset_name, 'TRAIN', problem)
        dataset['TEST' + problem] = get_dataset_split(
            dataset, dataset_name, 'TEST', problem)
        dataset['SCORE' + problem] = get_dataset_split(
            dataset, dataset_name, 'TEST', problem, targets=True)
