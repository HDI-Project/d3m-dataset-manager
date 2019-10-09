<p align="left">
<img width=15% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/Logo_DAI_highres.png" alt=“DAI-Lab” />
<i>An open source project from Data to AI Lab at MIT.</i>
</p>

[![PyPI Shield](https://img.shields.io/pypi/v/d3m-dataset-manager.svg)](https://pypi.python.org/pypi/d3m-dataset-manager)
[![Downloads](https://pepy.tech/badge/d3m-dataset-manager)](https://pepy.tech/project/d3m-dataset-manager)
[![Travis CI Shield](https://travis-ci.org/HDI-Project/d3m-dataset-manager.svg?branch=master)](https://travis-ci.org/HDI-Project/d3m-dataset-manager)
<!--[![Coverage Status](https://codecov.io/gh/HDI-Project/d3m-dataset-manager/branch/master/graph/badge.svg)](https://codecov.io/gh/HDI-Project/d3m-dataset-manager)-->

# D3M Dataset Manager

The D3M Dataset Manager is a command line tool and python package to generate and manage
datasets in the D3M format.

- Documentation: https://HDI-Project.github.io/d3m-dataset-manager
- Homepage: https://github.com/HDI-Project/d3m-dataset-manager

# Overview

The D3M Dataset Manager is a command line tool and python package to generate and manage
datasets in the D3M format.

It supports:

* downloading datasets from the D3M web repository or from S3 buckets
* uploading datasets to S3 buckets
* loading or saving datasets to local filesystem
* spliting datasets into TRAIN, TEST and SCORE subsets following the dataSplits.csv indexes

## Data Format

The D3M Dataset Schema, developed by MIT Lincoln Labs Laboratory for the DARPA's Data Driven
Discovery of Models Program, requires the data to be in plainly readable formats such as CSV files
or JPG images, and to be set within a folder hierarchy alongside some metadata specifications
in JSON format, which include information about all the data contained, as well as the problem
that we are trying to solve.

For more details about the schema and about how to format your data to be compliant with it,
please have a look at the [Schema Documentation](https://github.com/mitll/d3m-schema/tree/master/documentation)

# Install

## Install from PyPI

The easiest and recommended way to install the **D3M Dataset Manager** is using
[pip](https://pip.pypa.io/en/stable/):

```bash
pip install d3m-dataset-manager
```

This will pull and install the latest stable release from [PyPI](https://pypi.org/).

## Install from source

If you want to install the project from its sources, you can clone the repository and install it
by running `make install` on the `stable` branch:

```bash
git clone git@github.com:HDI-Project/d3m-dataset-manager.git
cd d3m-dataset-manager
git checkout stable
make install
```

## Install for Development

If you want to contribute to the project, a few more steps are required to make the project ready
for development.

Please head to the [Contributing Guide](https://HDI-Project.github.io/d3m-dataset-manager/contributing.html#get-started)
for more details about this process.

# Usage

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

## Command Line Options

The main element of the **D3M Dataset Manager** is the commadn `d3mdm`, which will be available
in your command line after installing the package.

This command supports the following options:

- **-i, --input** - D3M website, IPFS, S3 bucket or local folder.
- **-o, --output** - S3 bucket or local folder.
- **-l, --list** - List all available datasets in the indicated input.
- **-a, --all** - Get and process all available datasets in the indicated input.
- **-s, --split** - Split the dataset using the dataSplits.csv indexes.
- **-r, --raw** - Do not download the splitted subsets. `-s` option implicitly enables this one.
- **-f, --force** - Overwrite any existing datasets. If not enabled, existing datasets will be skipped.
- **-d, --dry-run** - Do not perform any real action. Only list them.
- **dataset names** - Name of the datasets o download. The `-a` option overrides them.

### Input and Output

The Input and Output options implicitely point at different locations depending on the format:

* **D3M**: `d3m:username:passsword`: password can be omitted, as well as username. Accepted only as Input.
  If omitted, the user will be asked to insert them later on.
* **IPFS**: `ipfs`: The datasets will be downloaded using an IPFS mirror of the D3M repository.
* **S3**: `s3://bucket-name/folder`: The datasets will be stored as a `.tar.gz` archive. If
  `folder` is not specified it defaults to `datasets`.
* **Local filesystem**: `local/filesystem/path`: The path must exist, otherwise it raises an error.

## Usage Examples

Download all datasets from D3M and store them as they are into S3 bucket named `d3m-data-dai`.
This will skip existing datasets.

```
d3m-dataset-manager -i d3m:a_username:a_password -o s3:d3m-data-dai -a
```

Download all datasets from the IPFS mirror, split them and store them in a local folder
`datasets`, overwriting any existing data.

This will prompt the user for the d3m password.

```
d3m-dataset-manager -i ipfs -o datasets -a -s -f
```

Download the datasets `185_baseball` and `32_wikiqa` from S3 bucket `bucket-name`
into local folder `data/datasets`. Overwrite the existing data.

```
d3m-dataset-manager -i s3://bucket-name -o data/datasets -f 185_baseball 32_wikiqa
```

# What's next?

For more details about **D3M Dataset Manager** and all its possibilities
and features, please check the [documentation site](https://HDI-Project.github.io/d3m-dataset-manager/).
