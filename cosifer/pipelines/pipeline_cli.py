"""COSIFER client pipeline."""
import os
import logging
from copy import deepcopy
from ..inferencers import INFERENCERS, RECOMMENDED_INFERENCERS
from ..combiners import COMBINERS, RECOMMENDED_COMBINER
from ..collections.interaction_table import interaction_table_from_gzip
from ..utils.data import read_data, read_gmt

logger = logging.getLogger(__name__.split('.')[-1])


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
    if methods is not None:
        selected_methods = set(RECOMMENDED_INFERENCERS).union(set(methods))
    # return dictionary containing only the chosen methods
    return dict(
        (method, deepcopy(INFERENCERS[method]))
        for method in set(INFERENCERS) & selected_methods
    )


def run_inference(data, selected_methods, output_directory):
    """
    Perform network inference of the data given a set of methods
    and save the predicted graphs in an output directory.

    Args:
        data (pd.DataFrame): input dataframe.
        selected_methods (dict): selected inference methods.
        output_directory (str): output directory.
    """

    for name, inferencer in selected_methods.items():
        try:
            output_filepath = '{}/{}.csv.gz'.format(output_directory, name)
            if not os.path.exists(output_filepath):
                logger.info('start inference with method {}'.format(name))
                inferencer.filepath = output_filepath
                inferencer.load()
                inferencer.infer_network(data)
                # NOTE: allow retraining on new data
                inferencer.trained = False
            else:
                logger.info(
                    'inference already run and stored in {}'.
                    format(output_filepath)
                )
        except Exception:
            logger.exception('error with inferencer {}'.format(name))


def get_interaction_tables(output_directory):
    """
    Transform graphs from the output directory into interaction tables.

    Args:
        output_directory (str): path to the output directory

    Returns:
        dict: interaction tables from each method in a dictionary.
    """
    interaction_tables_dict = dict()
    for filename in os.listdir(output_directory):
        if filename.endswith('.csv.gz'):
            method = filename.replace('.csv.gz', '')
            filepath = os.path.join(output_directory, filename)
            interaction_tables_dict[method] = interaction_table_from_gzip(
                filepath
            )
    return interaction_tables_dict


def run_combiner(combiner_name, interaction_tables_dict, output_directory):
    """
    Combine interaction tables received from every methods and
    save the interaction table in the output directory.

    Args:
        combiner_name (str): combiner type.
        interaction_tables_dict (dict): dictionary containing interaction
            tables from each method.
        output_directory (str): path to the output directory.
    """
    logger.info('combine interaction tables')
    try:
        output_filepath = '{}/{}.csv.gz'.format(
            output_directory, combiner_name
        )
        if not os.path.exists(output_filepath):
            logger.info(
                'start combination with method {}'.format(combiner_name)
            )
            combiner = deepcopy(
                COMBINERS.get(combiner_name, COMBINERS[RECOMMENDED_COMBINER])
            )
            combiner.filepath = output_filepath
            combiner.load()
            combiner.combine(interaction_tables_dict.values())
            # NOTE: allow retraining on new data
            combiner.trained = False
        else:
            logger.info(
                'combination already run and stored in {}'.
                format(output_filepath)
            )
    except Exception:
        logger.exception('error with combiner {}'.format(combiner_name))


def run(
    filepath,
    output_directory,
    standardize=True,
    samples_on_rows=True,
    sep='\t',
    fillna=0.,
    header=0,
    index_col=0,
    methods=None,
    combiner=None,
    gmt_filepath=None,
    **kwargs
):
    """
    Run COSIFER client pipeline.

    Args:
        filepath (str): path to the file.
        output_directory (str): path where to store the results.
        standardize (bool, optional): toggle data standardization.
            Defaults to True.
        samples_on_rows (bool, optional): flag to indicate whether data are
            following the format where each row represents a sample.
            Defaults to True.
        sep (str, optional): field separator. Defaults to '\t'.
        fillna (float, optional): value used to fill NAs. Defaults to 0.
        header (int, optional): line for the header in the input file.
            Defaults to 0.
        index_col (int, optional): column index for the input index.
            Defaults to 0.
        methods (list, optional): inference methods. Defaults to None, a.k.a.,
            only recommended methods.
        combiner (str, optional): combiner type. Defaults to None, a.k.a.,
            no combination.
        gmt_filepath (str, optional): GMT file containing feature sets.
            Defaults to None, a.k.a., no GMT file provided.
    """
    # ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
    # read the data
    _ = kwargs.pop('sep', None)
    _ = kwargs.pop('header', None)
    _ = kwargs.pop('index_col', None)
    data = read_data(
        filepath,
        standardize=standardize,
        samples_on_rows=samples_on_rows,
        sep=sep,
        header=header,
        index_col=index_col,
        fillna=fillna,
        **kwargs
    )
    # select the methods
    selected_methods = method_selection(methods)
    # optional gmt
    if gmt_filepath is not None:
        feature_sets = read_gmt(gmt_filepath)
    else:
        feature_sets = {'': set(data.columns)}
    logger.debug(feature_sets)
    # run inference and combination
    for feature_name, feature_set in feature_sets.items():
        # create a directory to store the results
        results_output_directory = os.path.join(output_directory, feature_name)
        os.makedirs(results_output_directory, exist_ok=True)
        # select features discarding missing ones
        matching_features = list(set(data.columns) & feature_set)
        if len(matching_features) > 2:
            # run the inference methods
            run_inference(
                data[matching_features], selected_methods,
                results_output_directory
            )
            if combiner is not None:
                # get the inferred tables
                tables = get_interaction_tables(results_output_directory)
                if len(tables) > 1:
                    # run the combination
                    run_combiner(combiner, tables, results_output_directory)
                elif len(tables):
                    logger.warn(
                        'skipping consenus since a single network has been inferred'
                    )
                else:
                    logger.warn(
                        'no networks to combine were found'
                    )
        else:
            logger.warn(
                'inference on less than three features is not supported'
            )
