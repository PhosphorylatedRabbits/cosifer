#! /bin/bash
set -e
# installing R dependencies
echo 'Installing R packages dependencies for cosifer.'
Rscript -e 'userdir <- unlist(strsplit(Sys.getenv("R_LIBS_USER"), .Platform$path.sep))[1L]; dir.create(userdir, recursive = TRUE);'
Rscript -e 'if (!require("git2r")) {install.packages("git2r", repos="https://cran.rstudio.com");}'
Rscript -e 'if (!require("devtools")) {install.packages("devtools", repos="https://cran.rstudio.com");}'
Rscript -e 'if (!require("BiocManager")) {install.packages("BiocManager", repos="https://cran.rstudio.com"); BiocManager::install(version = "3.10");}'
Rscript -e 'if (!require("JRF")) {install.packages("JRF", repos="https://cran.rstudio.com");}'
Rscript -e 'if (!require("FunChisq")) {install.packages("FunChisq", repos="https://cran.rstudio.com");}'
Rscript -e 'if (!require("GENIE3")) {BiocManager::install("GENIE3");}'
Rscript -e 'if (!require("lars")) {install.packages("lars", repos="https://cran.rstudio.com");}'
Rscript -e 'if (!require("reshape2")) {install.packages("reshape2", repos="https://cran.rstudio.com");}'
Rscript -e 'if (!require("doParallel")) {install.packages("doParallel", repos="https://cran.rstudio.com");}'
Rscript -e 'if (!require("doRNG")) {install.packages("doRNG", repos="https://cran.rstudio.com");}'
Rscript -e 'if (!require("minet")) {BiocManager::install("minet");}'
Rscript -e 'if (!require("SNFtool")) {install.packages("SNFtool", repos="https://cran.rstudio.com");}'
echo 'R dependencies installed.'
