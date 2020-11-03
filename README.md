# COSIFER - COnSensus Interaction Network InFErence Service

<p align="center">
  <img src="./docs/_static/logo.png" alt="cosifer-logo" width=500>
</p>

Inference framework for reconstructing networks using a consensus approach
between multiple methods and data sources.

The online documentation for the module can be found [here](https://phosphorylatedrabbits.github.io/cosifer).

## requirements

- Python >= 3.6
- R >= 3.6.0
- pip
- wget
- build-essential (make, g++, cmake)
- git
- libgit2

## installation

Install it using `pip` to use it as module:

```console
pip install git+https://github.com/PhosphorylatedRabbits/cosifer@master
```

Or install it via `pip` after cloning (suggested for development):

```console
cd cosifer
pip install -U -e .
```

### Note for Mac OS X

To install some of the requirements a compiler supporting [OpenMP](https://www.openmp.org/) is needed.
We suggest to use [brew] to install it and use it for the compilation as follows:

```console
brew install gcc  # this might take time
CC=/usr/local/bin/g++-9 pip install git+https://github.com/PhosphorylatedRabbits/cosifer@master
```

## COSIFER executable script

The COSIFER executable accept the following arguments:

```console
usage: cosifer [-h] -i FILEPATH -o OUTPUT_DIRECTORY [--standardize]
               [--no-standardize] [--samples_on_rows] [--sep SEP]
               [--fillna FILLNA] [--header HEADER] [--index INDEX]
               [--methods METHODS] [--combiner COMBINER]
               [--gmt_filepath GMT_FILEPATH]

Run COSIFER to perform network inference on given data.

optional arguments:
  -h, --help            show this help message and exit
  -i FILEPATH, --filepath FILEPATH
                        path to the data.
  -o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY
                        path to the output directory.
  --standardize         flag that indicates whether to perform
                        standardization. Defaults behaviour is to standardize
                        the data.
  --no-standardize      flag that indicates whether to suppress
                        standardization. Defaults behaviour is to standardize
                        the data.
  --samples_on_rows     flag that indicates that data contain the samples on
                        rows. Defaults to False.
  --sep SEP             separator for the data. Defaults to .
  --fillna FILLNA       fill NAs with a given value. Defaults to 0..
  --header HEADER       header index in the data. Defaults to 0.
  --index INDEX         column index in the data. Defaults to None, a.k.a., no
                        index.
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

## examples

In the folder [examples](./examples), you can find applications of COSIFER consensus network inference.

## web service

Try out the COSIFER web service for free on [IBM Cloud](http://ibm.biz/cosifer-aas).

## citation

If you use COSIFER in you research please cite:

```bibtex
@article{10.1093/bioinformatics/btaa942,
    author = {Manica, Matteo and Bunne, Charlotte and Mathis, Roland and Cadow, Joris and Ahsen, Mehmet Eren and Stolovitzky, Gustavo A and Martínez, María Rodríguez},
    title = "{COSIFER: a python package for the consensus inference of molecular interaction networks}",
    journal = {Bioinformatics},
    year = {2020},
    month = {11},
    issn = {1367-4803},
    doi = {10.1093/bioinformatics/btaa942},
    url = {https://doi.org/10.1093/bioinformatics/btaa942},
    note = {btaa942},
    eprint = {https://academic.oup.com/bioinformatics/advance-article-pdf/doi/10.1093/bioinformatics/btaa942/34088187/btaa942.pdf},
}
```
