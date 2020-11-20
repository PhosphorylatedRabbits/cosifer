
#!/usr/bin/env python3
"""Run gui pipeline with all inferencers for each combiner."""
import os
import pandas as pd
from cosifer.combiners import COMBINERS
from cosifer.inferencers import INFERENCERS
from cosifer.pipelines.pipeline_cli import (
    run_inference, get_interaction_tables, run_combiner
)

# depends on docker mount
df = pd.read_csv('/data/demo/data_matrix.csv')
df.head()

output_directory = '/tmp/test/'
os.makedirs(output_directory, exist_ok=False)

run_inference(df, INFERENCERS, output_directory)
tables = get_interaction_tables(output_directory)
for combiner_name in COMBINERS.keys():
    run_combiner(combiner_name, tables, output_directory)

expected_number_of_networks = len(INFERENCERS) + len(COMBINERS)
_, _, files = next(os.walk(output_directory))
number_of_networks = len(files)

if expected_number_of_networks != number_of_networks:
    raise AssertionError(
        f'Only {number_of_networks} out of {expected_number_of_networks} '
        'networks were produced!\n'
        f'The following were found:\n{files}'
    )
