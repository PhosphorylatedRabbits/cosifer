# COSIFER executable script

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
