# COSIFER - COnSensus Interaction Network InFErence Service

<p align="center">
  <img src="./docs/_static/logo.png" alt="cosifer-logo" width=500>
</p>

Inference framework for reconstructing networks using a consensus approach
between multiple methods and data sources.

## requirements

- Python >= 3.4
- R >= 3.3.0
- pip
- wget
- build-essential (make, g++, cmake)
- git
- libgit2

## installation

Install it using `pip` to use it as module:

```console
pip install git+https://github.com/TBD/cosifer@master
```

Or install it via `pip` after cloning (suggested for development):

```console
cd cosifer
pip install -U -e .
```

# COSIFER executable script

The COSIFER executable accept the following arguments:

```console
usage: cosifer [-h] --filepath FILEPATH --output_directory OUTPUT_DIRECTORY
               [--standardize STANDARDIZE] [--samples_on_rows SAMPLES_ON_ROWS]
               [--sep SEP] [--fillna FILLNA] [--header HEADER] [--index INDEX]
               [--methods METHODS] [--combiner COMBINER]
               [--gmt_filepath GMT_FILEPATH]

Run COSIFER to perform network inference on given data.

optional arguments:
  -h, --help            show this help message and exit
  --filepath FILEPATH   path to the data.
  --output_directory OUTPUT_DIRECTORY
                        path to the output directory.
  --standardize STANDARDIZE
                        standardize the data. Defaults to True.
  --samples_on_rows SAMPLES_ON_ROWS
                        rows in the data contain the samples. Defaults to
                        True.
  --sep SEP             separator for the data. Defaults to .
  --fillna FILLNA       fill NAs with a given value. Defaults to 0..
  --header HEADER       header index in the data. Defaults to 0.
  --index INDEX         column index in the data. Defaults to 0.
  --methods METHODS     methods which should be used for network inference. If
                        no methods are passed, it defaults to the following
                        set of methods: ['pearson', 'spearman', 'aracne',
                        'mrnet', 'clr', 'funchisq']
  --combiner COMBINER   method used for consensus network inference. Defaults
                        to: summa
  --gmt_filepath GMT_FILEPATH
                        optional GMT file to perform inference on multiple
                        gene sets.
```

