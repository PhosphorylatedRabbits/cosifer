"""COSIFER GUI pipeline."""
import sys
import os
import logging
from copy import deepcopy
from ..inferencers import INFERENCERS, RECOMMENDED_INFERENCERS
from ..combiners import COMBINERS, RECOMMENDED_COMBINER

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def method_selection(methods=None):
    """
    Select inference methods.

    Args:
        methods (list): list of inferencers to run. Defaults to None,
            a.k.a., use defaults.

    Returns:
        dict: a dictionary keyed by method name and inferencers as values.
    """
    # add desired methods to list of methods and removal of duplicates
    selected_methods = (
        set(INFERENCERS).intersection(set(methods))
        if methods else RECOMMENDED_INFERENCERS
    )
    # return dictionary containing only the chosen methods
    return dict(
        (method, deepcopy(INFERENCERS[method]))
        for method in selected_methods
    )


def run_inference(data, selected_methods):
    """
    Perform network inference of the data given a set of methods
    and return the predicted graphs.

    Args:
        data (pd.DataFrame): input dataframe.
        selected_methods (dict): selected inference methods.

    Returns:
        dict: interaction tables inferred with the selected methods.
    """
    interaction_tables_dict = dict()
    for name, inferencer in selected_methods.items():
        logger.info('start inference with method {}'.format(name))
        try:
            inferencer.infer_network(data)
            interaction_tables_dict[name] = (
                inferencer.graph.to_interaction_table()
            )
            logger.info('inference with {} was successful.'.format(name))
        except Exception:
            logger.exception('inference with {} failed.'.format(name))
    return interaction_tables_dict


def run_combiner(combiner_name, interaction_tables_dict, results_filepath):
    """
    Combine interaction tables received from every methods and
    save the interaction table to a output file.

    Args:
        combiner_name (str): combiner type.
        interaction_tables_dict (dict): dictionary containing interaction
            tables from each method.
        results_filepath (str): path to the results.
    """
    logger.info('combine interaction tables')
    try:
        logger.info('start combination with method {}'.format(
            combiner_name
        ))
        combiner = deepcopy(
            COMBINERS.get(combiner_name, COMBINERS[RECOMMENDED_COMBINER])
        )
        combiner.filepath = results_filepath
        combiner.load()
        combiner.combine(interaction_tables_dict.values())
    except Exception:
        logger.exception('error with combiner {}'.format(combiner_name))


def run(data, results_filepath, methods=None, combiner='summa'):
    """
    Run COSIFER GUI pipeline.

    Args:
        data (pd.DataFrame): data used for inference.
        results_filepath (str): path where to store the results.
        methods (list, optional): inference methods. Defaults to None, a.k.a.,
            only recommended methods.
        combiner (str, optional): combiner type. Defaults to summa.
    """
    # make sure the output exists
    os.makedirs(os.path.dirname(results_filepath), exist_ok=True)

    # decide on which network inference methods to perform
    selected_methods = method_selection(methods)

    if len(selected_methods) < 1:
        raise RuntimeError('No valid methods passed!')

    # run inference methods
    interaction_tables_dict = run_inference(data, selected_methods)
    number_of_inferred_networks = len(interaction_tables_dict)

    if number_of_inferred_networks < 2:
        if number_of_inferred_networks < 1:
            raise RuntimeError('No inferred networks!')
        # a single method produced a valid network
        _, interaction_table = next(iter(interaction_tables_dict.items()))
        interaction_table.df.to_csv(results_filepath, compression='gzip')
    else:
        # run a consensus strategy to combine the results of the single methods
        run_combiner(combiner, interaction_tables_dict, results_filepath)
