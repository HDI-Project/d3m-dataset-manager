# -*- coding: utf-8 -*-

import gc
import logging
import os
from getpass import getpass

import d3m
import local
import s3
from splitter import add_dataset_splits

LOGGER = logging.getLogger(__name__)


def logging_setup(verbosity=1):
    logger = logging.getLogger()
    log_level = (3 - verbosity) * 10
    fmt = '%(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    logger.setLevel(log_level)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def parse_s3_path(path):
    parts = path[5:].split('/', 1)
    bucket = parts[0]
    folder = parts[1] if len(parts) > 1 else 'datasets'
    return bucket, folder


def get_input_manager(args):
    if args.input.startswith('d3m:'):
        input_args = args.input[4:].split(':')
        username = input_args[0]
        password = input_args[1:]

        if not username:
            username = input('Username: ')

        if password:
            password = password[0]

        if not password:
            password = getpass()

        return d3m.D3MManager(username, password, skip_sublevels=args.skip_sublevels)

    elif args.input.startswith('ipfs'):
        return d3m.IPFSManager(skip_sublevels=args.skip_sublevels)

    elif args.input.startswith('s3://'):
        bucket, folder = parse_s3_path(args.input)
        return s3.S3Manager(bucket, folder, skip_sublevels=args.skip_sublevels)

    elif os.path.isdir(args.input):
        return local.LocalManager(args.input, args.skip_sublevels)

    else:
        raise Exception('Invalid Input: {}'.format(args.input))


def get_output_manager(args):
    if args.output.startswith('s3://'):
        bucket, folder = parse_s3_path(args.output)
        return s3.S3Manager(bucket, folder)

    elif os.path.isdir(args.output):
        return local.LocalManager(args.output)

    else:
        raise Exception('Invalid Output: {}'.format(args.output))


def process_dataset(dataset_name, input_manager, output_manager, split, raw):
    raw = raw or split
    dataset = input_manager.load(dataset_name, raw=raw)
    if split:
        add_dataset_splits(dataset, dataset_name)

    output_manager.write(dataset, dataset_name)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='D3M dataset manager')

    # Logging
    parser.add_argument('-v', '--verbose', action='count', default=0)

    # Input
    parser.add_argument('-i', '--input', required=True,
                        help='Local folder, s3:bucket or d3m:username:password.')

    # Output
    output_or_list = parser.add_mutually_exclusive_group()
    output_or_list.add_argument('-o', '--output', help='Local folder or s3:bucket:folder')
    output_or_list.add_argument('-l', '--list', action='store_true',
                                help='List all datasets found in input')

    # Process options
    parser.add_argument('-a', '--all', action='store_true',
                        help='Process all datasets from Input')
    parser.add_argument('-s', '--split', action='store_true',
                        help='Compute and store the dataset splits.')
    parser.add_argument('-r', '--raw', action='store_true',
                        help='Do not download the dataset splits.')
    parser.add_argument('-S', '--skip-sublevels', action='store_true',
                        help='Skip dataset sublevels. For debug purposes')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Overwrite previously downloaded datasets')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Do not perform any real action. Only name them.')
    # TODO: add cleanup option: Delete the dataset before saving

    parser.add_argument('dataset', type=str, nargs='*', help='Datasets to process.')

    args = parser.parse_args()

    logging_setup(args.verbose)

    input_manager = get_input_manager(args)

    if args.list:
        for dataset in input_manager.datasets():
            print(dataset)

    else:
        if args.all:
            datasets = input_manager.datasets()

        else:
            datasets = args.dataset

        if not datasets:
            print('Please provide at least a dataset name')

        else:
            output_manager = get_output_manager(args)
            for dataset in datasets:
                if args.force or not output_manager.exists(dataset):
                    print('Copying dataset {} from {} to {}'.format(
                        dataset, args.input, args.output))
                    if not args.dry_run:
                        process_dataset(
                            dataset, input_manager, output_manager, args.split, args.raw)
                        gc.collect()

                else:
                    print('Dataset {} already exists. Use --force to overwrite.'.format(dataset))
