"""Combiner module."""
from .cit import (
    CombineInteractionTables,
    hard_mean_scaled_ranks_table, hard_mean_table,
    mean_scaled_ranks_table, mean_table,
    median_scaled_ranks_table, median_table,
    max_scaled_ranks_table, max_table,
    min_scaled_ranks_table, min_table,
    WOC, WOCHard
)
from .summa import Summa
from .snf import SNF


CIT_FUNCTIONS = {
    'hard-mean-scaled-ranks': hard_mean_scaled_ranks_table,
    'hard-mean': hard_mean_table,
    'mean-scaled-ranks': mean_scaled_ranks_table,
    'mean': mean_table,
    'median-scaled-ranks': median_scaled_ranks_table,
    'median': median_table,
    'max-scaled-ranks': max_scaled_ranks_table,
    'max': max_table,
    'min-scaled-ranks': min_scaled_ranks_table,
    'min': min_table,
}

COMBINERS = {
    'woc': CombineInteractionTables(
        combine_tables=mean_scaled_ranks_table, name='woc'
    ),
    'woc_hard': CombineInteractionTables(
        combine_tables=hard_mean_scaled_ranks_table, name='woc_hard'
    ),
    'summa': Summa(name='summa'),
    'snf': SNF(name='snf')
}

COMBINER_TYPES = {
    'summa': Summa,
    'snf': SNF,
    'woc': WOC,
    'woc_hard': WOCHard
}

RECOMMENDED_COMBINER = 'summa'
