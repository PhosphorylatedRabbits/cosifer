"""Inferencer module."""
from .correlation import Correlation
from .funchisq import FunChisq
from .aracne import Aracne
from .glasso import Glasso
from .jrf import JointRandomForest
from .genie3 import GENIE3
from .tigress import TIGRESS
from .mrnet import MRNET
from .clr import CLR


INFERENCERS = {
    'spearman':
        Correlation(
            method='spearman', correction='b-h', confidence_threshold=.05
        ),
    'pearson':
        Correlation(
            method='pearson', correction='b-h', confidence_threshold=.05
        ),
    'funchisq':
        FunChisq(
            correction='b-h', confidence_threshold=.05,
            k_min=3, k_max=5, n_init=10
        ),
    'aracne':
        Aracne(estimator='spearman'),
    'glasso':
        Glasso(),
    'jrf':
        JointRandomForest(),
    'genie3':
        GENIE3(
            tree_method='RF', k='sqrt', n_trees=1000, n_cores=1
        ),
    'tigress':
        TIGRESS(
            k=-1, alpha=0.2, n_steps_lars=5,
            n_bootstrap=1000, scoring='area', verbose=False,
            use_parallel=False, n_cores=1
        ),
    'clr':
        CLR(estimator='spearman'),
    'mrnet':
        MRNET(estimator='spearman')
}


RECOMMENDED_INFERENCERS = [
    'pearson', 'spearman', 'aracne', 'mrnet', 'clr', 'funchisq'
]
