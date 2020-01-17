"""GENIE3 inferencer."""
import logging
import pandas as pd
from rpy2.robjects import pandas2ri, numpy2ri, r, globalenv
from rpy2.robjects.packages import importr
from rpy2.rinterface import NULL
from ..collections.graph import Graph
from .network_inferencer import NetworkInferencer

logger = logging.getLogger(__name__.split('.')[-1])


class GENIE3(NetworkInferencer):
    """
    GENIE3 inferencer.

    Attributes:
        tree_method (str): tree method.
        k (str): k criterion.
        n_trees (int): number of trees.
        regulators (object): known regulators.
        targets (object): known targets.
        n_cores (int): number of cores.
        verbose (bool): toggle verbosity.
        method (str): name of the method.
    """
    def __init__(
        self,
        tree_method='RF',
        k='sqrt',
        n_trees=1000,
        regulators=NULL,
        targets=NULL,
        n_cores=4,
        verbose=False,
        method='GENIE3',
        **kwargs
    ):
        self.tree_method = tree_method
        self.k = k
        self.n_trees = n_trees
        self.regulators = regulators
        self.targets = targets
        self.n_cores = n_cores
        self.verbose = verbose
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
        genie3 = importr('GENIE3')
        importr('foreach')
        importr('doParallel')
        # transform pandas dataframe into GENIE3 input format
        globalenv['r_matrix'] = numpy2ri.py2ri(data.T.values)
        globalenv['r_rows'] = data.columns
        globalenv['r_cols'] = data.index
        r('''
        rownames(r_matrix) <- c(r_rows)
        colnames(r_matrix) <- c(r_cols)
        ''')
        expr_matrix = globalenv['r_matrix']
        # run GENIE3
        values = numpy2ri.ri2py(
            genie3.GENIE3(
                expr_matrix, self.regulators, self.targets, self.tree_method,
                self.k, self.n_trees, self.n_cores, self.verbose
            )
        )
        weight_matrix = pd.DataFrame(
            values, columns=data.columns, index=data.columns
        )
        self.graph = Graph(adjacency=weight_matrix)
        logger.debug('inferred with {}'.format(self.method))

    def __str__(self):
        """
        Get the name of the inferencer.

        Returns:
            str: name of the inferencer: genie3.
        """
        return 'genie3'
