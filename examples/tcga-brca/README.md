# TCGA BRCA

In the following we will use COSIFER to analyze a breast cancer cohort from TCGA.
This tutorial assumes that the user has already followed the installation instruction reported [here](../../README.md).

**NOTE:** Keep in mind that the commands are assumed to be run in the folder containing this README.md file. In case you want to use a custom location, just updates the path accordingly.

## data

Herein, we consider two different data types:

- RPPA proteomic data: [rppa-processed.tsv.zip](./rppa-processed.tsv.zip)
- RNASeq data: [rnaseq-processed.tsv.zip](./rnaseq-processed.tsv.zip)

Both data files have been obtained by processing data downloaded from the [Firebrowse API](http://firebrowse.org/api-docs/).
The processing was lmited to mapping identifiers for molecular entities to gene names.

## setup

Create a folder where to store the results:

```console
mkdir -p results
```

## infer a network from proteomic data

Inferring networks using COSIFER is as easy as running a command line one-liner:

```console
cosifer -i rppa-processed.tsv.zip --index 0 -o results/rppa/
```

In the output folder you can find all the networks inferred, including the consensus network:

```console
ls -rt1 results/rppa
pearson.csv.gz
mrnet.csv.gz
aracne.csv.gz
spearman.csv.gz
clr.csv.gz
funchisq.csv.gz
summa.csv.gz
```

COSIFER used the default inference methods (selected based on runtime performance) and the default consensus method: SUMMA.

The user can easily use a custom set of methods and a different combiner just tweaking the parameters:

```console
cosifer -i rppa-processed.tsv.zip --index 0 --methods pearson --methods aracne --methods clr --methods mrnet --combiner snf -o results/rppa-custom
```

```console
ls -rt1 results/rppa-custom
mrnet.csv.gz
pearson.csv.gz
aracne.csv.gz
clr.csv.gz
snf.csv.gz
```
