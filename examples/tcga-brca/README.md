# TCGA BRCA

In the following we will use COSIFER to infer networks from a breast cancer cohort from TCGA.
This tutorial assumes that the user has already followed the installation instructions reported [here](../../README.md).

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

Here we consider the task of inferring a network on the whole set of proteomic data available from the RPPA measurements.

Inferring a network using COSIFER is as easy as running a command line one-liner:

```console
cosifer -i rppa-processed.tsv.zip --index 0 -o results/rppa/
```

**NOTE:** COSIFER automatically handles compressed files in various formats. For details see the documentation of [`pandas.read_csv`](https://pandas.pydata.org/pandas-docs/version/0.23.4/generated/pandas.read_csv.html).

In the output folder you can find all the networks inferred in compressed edge list format, including the consensus network:

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

The `.csv.gz` files produced follow a standard compressed edge list format to ease later stages of post-processing:

```console
gzcat results/rppa/summa.csv.gz | head
,e1,e2,intensity
YWHAE<->YWHAZ,YWHAE,YWHAZ,0.4753944363747977
YWHAB<->YWHAZ,YWHAB,YWHAZ,0.4905812857253884
YWHAB<->YWHAE,YWHAB,YWHAE,0.7839150777498404
YBX1<->YWHAZ,YBX1,YWHAZ,0.8143271655863514
YBX1<->YWHAE,YBX1,YWHAE,0.5480472837215761
YBX1<->YWHAB,YBX1,YWHAB,0.17802127491882738
YAP1<->YWHAZ,YAP1,YWHAZ,0.5130864844208401
YAP1<->YWHAE,YAP1,YWHAE,0.5187274944588639
YAP1<->YWHAB,YAP1,YWHAB,0.1812873425719532
```

**NOTE:** this format allows to associate weights to edges between entities. Since the vast majority of the inference methods implemented in COSIFER assumes undirected graphs, also the networks inferred and combined via consensus are undirected.

In this run, COSIFER used the default inference methods (selected based on runtime performance) and the default consensus method: [SUMMA](http://doi.org/10.1089/cmb.2019.0348).

The user can easily use a custom set of methods and a different combiner (e.g., [SNF](http://compbio.cs.toronto.edu/SNF/SNF/Software.html)) just tweaking the parameters:

```console
cosifer -i rppa-processed.tsv.zip --index 0 --methods pearson --methods aracne --methods clr --methods mrnet --combiner snf -o results/rppa-custom
```

The outputs produced are stored following the same convention used in the default case:

```console
ls -rt1 results/rppa-custom
mrnet.csv.gz
pearson.csv.gz
aracne.csv.gz
clr.csv.gz
snf.csv.gz
```

## infer pathway-specific networks from RNASeq data

Here we consider the task of inferring networks by considering pathway-specific transcriptomic data from RNASeq measurements and a `.gmt` file from [GSEA](https://www.gsea-msigdb.org/gsea/msigdb/collections.jsp#H).

First download the hallmark gene sets (v7.0) from this [link](https://www.gsea-msigdb.org/gsea/msigdb/download_file.jsp?filePath=/msigdb/release/7.0/h.all.v7.0.symbols.gmt) (email registration required), and store the `.gmt` file in this folder:

```console
ls -1
README.md
h.all.v7.0.symbols.gmt
requirements.txt
results
rnaseq-processed.tsv.zip
rppa-processed.tsv.zip
```

To perform the inference for each pathway contained in the `.gmt` file, simply run:

```console
cosifer -i rnaseq-processed.tsv.zip --index 0 -o results/rnaseq/ --gmt_filepath h.all.v7.0.symbols.gmt
```

**NOTE:** this will take time since it will run inference and consensus pipelines for all the 50 hallmark gene sets.

After the execution the results for each gene set are stored in different folders:

```console
ls -1 results/rnaseq
HALLMARK_ADIPOGENESIS
HALLMARK_ALLOGRAFT_REJECTION
HALLMARK_ANDROGEN_RESPONSE
HALLMARK_ANGIOGENESIS
...
HALLMARK_UV_RESPONSE_DN
HALLMARK_UV_RESPONSE_UP
HALLMARK_WNT_BETA_CATENIN_SIGNALING
HALLMARK_XENOBIOTIC_METABOLISM
```

Where each folder follows the usual result format, for example:

```console
ls -rt1 results/rnaseq/HALLMARK_P53_PATHWAY
pearson.csv.gz
spearman.csv.gz
aracne.csv.gz
mrnet.csv.gz
clr.csv.gz
funchisq.csv.gz
summa.csv.gz
```
