[![][pypi-img]][pypi-url] [![][travis-img]][travis-url]

# Dataset Manager

Dataset Manager is a tool to generate and manage datasets in custom formats.

- Free software: MIT license
- Documentation: https://HDI-Project.github.io/dataset-manager

[travis-img]: https://travis-ci.org/HDI-Project/dataset-manager.svg?branch=master
[travis-url]: https://travis-ci.org/HDI-Project/dataset-manager
[pypi-img]: https://img.shields.io/pypi/v/dataset-manager.svg
[pypi-url]: https://pypi.python.org/pypi/dataset-manager

It supports:

* downloading datasets from the D3M repository or from S3 buckets
* uploading datasets to S3 buckets
* loading or saving datasets to local filesystem
* spliting datasets into TRAIN, TEST and SCORE subsets following the dataSplits.csv indexes

## Installation

The simplest and recommended way to install Dataset Manager is using `pip`:

```bash
pip install dataset-manager
```

Alternatively, you can also clone the repository and install it from sources for development:

```bash
git clone git@github.com:HDI-Project/dataset-manager.git
cd dataset-manager
pip install -e .[dev]
```

## Configuration

### D3M Repository

In order to interact with the D3M repository you will need the user and the password
user to log into https://datadrivendiscovery.org/data

### S3 Bucket

In order to interact with the S3 buckets, you will need to configure your S3 access
following the instructions from http://boto3.readthedocs.io/en/latest/guide/quickstart.html

In most cases, it will be enough to create the file `~/.aws/credentials:`
with the following contents:

```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

## Usage

The main script is the `download_manager/download_manager.py`, which supports the following options:

- **-i, --input** - D3M website, IPFS, S3 bucket or local folder.
- **-o, --output** - S3 bucket or local folder.
- **-l, --list** - List all available datasets in the indicated input.
- **-a, --all** - Get and process all available datasets in the indicated input.
- **-s, --split** - Split the dataset using the dataSplits.csv indexes.
- **-r, --raw** - Do not download the splitted subsets. `-s` option implicitly enables this one.
- **-f, --force** - Overwrite any existing datasets. If not enabled, existing datasets will be skipped.
- **-d, --dry-run** - Do not perform any real action. Only list them.
- **dataset names** - Name of the datasets o download. The `-a` option overrides them.

## Input and Output

The Input and Output options implicitely point at different locations depending on the format:

* **D3M**: `d3m:username:passsword`: password can be omitted, as well as username. Accepted only as Input.
If omitted, the user will be asked to insert them later on.
* **IPFS**: `ipfs`: The datasets will be downloaded using an IPFS mirror of the D3M repository.
* **S3**: `s3://bucket-name/folder`: The datasets will be stored as a `.tar.gz` archive. If `folder` is not specified it defaults to `datasets`.
* **Local filesystem**: `local/filesystem/path`: The path must exist, otherwise it raises an error.

## Usage Example

Download all datasets from D3M and store them as they are into S3 bucket named `d3m-data-dai`.
This will skip existing datasets.

```
python dataset_manager/cli.py -i d3m:a_username:a_password -o s3:d3m-data-dai -a
```

Download all datasets from the IPFS mirror, split them and store them in a local folder `datasets`, overwriting
any existing data.
This will prompt the user for the d3m password.

```
python dataset_manager/cli.py -i ipfs -o datasets -a -s -f
```

Download the datasets `185_baseball` and `32_wikiqa` from S3 bucket `bucket-name`
into local folder `data/datasets`. Overwrite the existing data.

```
python dataset_manager/cli.py -i s3://bucket-name -o data/datasets -f 185_baseball 32_wikiqa
```
