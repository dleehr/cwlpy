# cwlpy

[![Build Status](https://travis-ci.org/dleehr/cwlpy.svg?branch=master)](https://travis-ci.org/dleehr/cwlpy)

Python library for working with CWL documents, backed by schema-salad codegen.

This is a work-in-progress.

## Contents

- **generate_cwl_schema.sh**: Script to generate python classes using schema-salad, from the CWL standard
- **cwl_schema.py**: Auto-generated python classes from schema salad
- **cwlpy**: Subclasses of auto-generated classes for building up CWL objects programatically
- **example.py**: Example script using cwlpy to build a workflow and connect steps/inputs/outputs

## Example Usage


```
from cwlpy import Workflow, WorkflowStep as Step, WorkflowStepConnection as Connection
from ruamel import yaml

# https://github.com/common-workflow-language/cwl-v1.1/blob/master/tests/revsort.cwl

########################################
# Create workflow and steps
########################################

workflow = Workflow('revsort')
rev_step = Step('rev', run='revtool.cwl')
sort_step = Step('sorted', run='sorttool.cwl')

# Add steps by chaining
workflow.step(rev_step).step(sort_step)

########################################
# Connect workflow and steps
########################################

# workflow.input -> rev_step.input
workflow.connect_input(rev_step, 'input', 'input')
# workflow.reverse_sort -> sort_step.output
workflow.connect_input(sort_step, 'reverse_sort', 'reverse')
# rev_step.output -> sort_step.input
workflow.connect_steps(rev_step, sort_step, 'output','input')
# sort_step.output -> workflow.output
workflow.connect_output(sort_step, 'output', 'output')

print(yaml.safe_dump(workflow.save(), default_flow_style=False))
```
