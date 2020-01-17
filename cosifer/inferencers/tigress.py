"""TIGRESS inferencer."""
import logging
import numpy as np
from rpy2.robjects import pandas2ri, r, globalenv
from rpy2.robjects.packages import importr
from rpy2.rinterface import NULL
from ..collections.interaction_table import InteractionTable
from .network_inferencer import NetworkInferencer

logger = logging.getLogger(__name__.split('.')[-1])


class TIGRESS(NetworkInferencer):
    """
    TIGRESS inferencer.

    Attributes:
        tf_list (object): list of transcription factor.
        k (int): number of edges to return.
        alpha (float): alpha parameter.
        n_step_lars (int): number of LARS steps.
        n_bootstrap (int): bootstrap number.
        scoring (str): scoring criterion.
        verbose (bool): toggle verbosity.
        use_parallel (bool): enable parallelism.
        n_cores (int): number of cores.
        method (str): name of the method.
    """
    def __init__(
        self,
        tf_list=NULL,
        k=-1,
        alpha=0.2,
        n_steps_lars=5,
        n_bootstrap=1000,
        scoring="area",
        verbose=False,
        use_parallel=True,
        n_cores=4,
        method='TIGRESS',
        **kwargs
    ):
        """
        Initialize TIGRESS inferencer.

        Args:
            tf_list (object, optional): list of transcription factor.
                Defaults to NULL.
            k (int, optional): number of edges to return. Defaults to -1.
            alpha (float, optional): alpha parameter. Defaults to 0.2.
            n_steps_lars (int, optional): number of LARS steps. Defaults to 5.
            n_bootstrap (int, optional): bootstrap number. Defaults to 1000.
            scoring (str, optional): scoring criterion. Defaults to "area".
            verbose (bool, optional): toggle verbosity. Defaults to False.
            use_parallel (bool, optional): enable parallelism.
                Defaults to True.
            n_cores (int, optional): number of cores. Defaults to 4.
            method (str, optional): name of the method. Defaults to 'TIGRESS'.
        """
        self.tf_list = tf_list
        self.k = k
        self.alpha = alpha
        self.n_steps_lars = n_steps_lars
        # division of number of bootstrap samples by 2 since TIGRESS runs two
        # models for each bootstrap
        self.n_bootstrap = int(np.divide(n_bootstrap, 2))
        self.scoring = scoring
        self.verbose = verbose
        self.use_parallel = use_parallel
        self.n_cores = n_cores
        self.method = method
        super().__init__(**kwargs)

    def _infer_network(self, data):
        """
        Infer the network.

        Args:
            data (pd.DataFrame): data to be used for the inference.
        """
        # activate implicit conversion from pandas to R objects
        pandas2ri.activate()
        importr('lars')
        importr('parallel')
        # stability selection in the spirit of Meinshausen & Buhlman
        # authors: Anne-Claire Haury and Jean-Philippe Vert
        r('''
        stabilityselection <- function(x, y, nbootstrap=100, nstepsLARS=20, alpha=0.2, scoring="area")
        {
            n <- nrow(x)
            p <- ncol(x)
            halfsize <- as.integer(n / 2)
            freq <- matrix(0, nstepsLARS, p)

            for (i in seq(nbootstrap)) {
                # Randomly reweight each variable
                        xs <- t(t(x) * runif(p, alpha, 1))

            # Ramdomly split the sample in two sets
            perm <- sample(n)
            i1 <- perm[1:halfsize]
            i2 <- perm[(halfsize + 1):n]

            # run LARS on each randomized, sample and check which variables are selected
            r <- lars(xs[i1,], y[i1], max.steps = nstepsLARS, normalize = FALSE, trace = FALSE, use.Gram = FALSE)
            freq <-freq + abs(sign(r$beta[2:(nstepsLARS + 1), ]))
            r <- lars(xs[i2,], y[i2], max.steps = nstepsLARS, normalize = FALSE, trace = FALSE, use.Gram = FALSE)
            freq <-freq + abs(sign(r$beta[2:(nstepsLARS + 1), ]))
        }
        # normalize frequence in [0,1] to get the stability curves
        freq <- freq / (2 * nbootstrap)
        # Compute normalized area under the stability curve
        if (scoring == "area")
        score <- apply(freq, 2, cumsum) / seq(nstepsLARS)
        else
        score <- apply(freq, 2, cummax)

        invisible(score)
        }
        tigress <- function(expdata, tflist=NULL, K=-1 , alpha=0.2, nstepsLARS=5, nbootstrap=100, scoring="area", verb=FALSE, useparallel=TRUE, n_cores=4)
        {
            # Gene names
            genenames <- colnames(expdata)
            ngenes <- length(genenames)
            # If needed, load TF list
            if (is.null(tflist)) {
                # No TF list or file provided, we take all genes as TF
                tflist <- genenames
            } else if (length(tflist) == 1 && is.na(match(tflist, genenames))) {
                # If this is a single string which is not a gene name, then it should be a file name
                tflist <- read.table(tflist, header=0)
                tflist <- as.matrix(tflist)[,1]
            }
            # Make sure there are no more steps than variables
            if (nstepsLARS>length(tflist)-1){
                nstepsLARS<-length(tflist)-1
                if (nstepsLARS==0){cat('Too few transcription factors! \n', stderr())}
                if (verb){
                cat(paste('Variable nstepsLARS was changed to: ', nstepsLARS, '\n')) }}
            # Locate TF in gene list by matching their names
            ntf <- length(tflist)
            tfindices <- match(tflist,genenames)
            if (max(is.na(tfindices))) {
                stop('Error: Could not find all TF in the gene list!')
            }
            # Number of predictions to return
            Kmax <- ntf * ngenes
            if (K==-1) K <- Kmax
            K <- min(K, Kmax)
            # Prepare scoring matrix
            scorestokeep <- 1
            score <- list()
            # A small function to score the regulators of a single gene
            stabselonegene <- function(itarget) {
                if (verb) {
                    cat('.')
                    }
                # Name of the target gene
                targetname <- genenames[itarget]
                # Find the TF to be used for prediction (all TF except the target if the target is itself a TF)
                predTF <- tfindices[!match(tflist, targetname, nomatch=0)]
                r <- stabilityselection(as.matrix(expdata[, predTF]), as.matrix(expdata[, itarget]), nbootstrap=nbootstrap, nsteps=nstepsLARS, alpha=alpha)
                sc <- array(0, dim=c(ntf, scorestokeep), dimnames = list(tflist, seq(scorestokeep)))
                sc[predTF,] <- t(r[nstepsLARS, ])
                invisible(sc)
            }
            # Treat target genes one by one
            if (useparallel) {
                score <- mclapply(seq(ngenes), stabselonegene, mc.cores=n_cores)
            } else {
                score <- lapply(seq(ngenes),stabselonegene)
            }
            # Rank scores
            edgepred <- list()
            for (i in seq(scorestokeep)) {
                # Combine all scores in a single vectors
                myscore <- unlist(lapply(score,function(x) x[,1,drop=FALSE]))
                ranki <- order(myscore,decreasing=TRUE)[1:K]
                edgepred[[i]] <- data.frame(list(tf=tflist[(ranki-1)%%ntf+1] , target=genenames[(ranki-1)%/%ntf+1] , score=myscore[ranki]))
            }
            return(edgepred)
        }
        ''')
        tigress = globalenv['tigress']
        interactions = pandas2ri.ri2py(
            tigress(
                pandas2ri.py2ri(data), self.tf_list, self.k, self.alpha,
                self.n_steps_lars, self.n_bootstrap, self.scoring,
                self.verbose, self.use_parallel, self.n_cores
            )[0]
        )
        interactions.columns = ['e1', 'e2', 'intensity']
        self.graph = InteractionTable(df=interactions).to_graph()
        logger.debug('inferred with {}'.format(self.method))

    def __str__(self):
        """
        Get the name of the inferencer.

        Returns:
            str: name of the inferencer: tigress.
        """
        return 'tigress'
