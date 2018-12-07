from cwlpy import Workflow, WorkflowStep as Step, WorkflowStepConnection as Connection
from ruamel import yaml

# https://github.com/common-workflow-language/cwl-v1.1/blob/master/tests/revsort.cwl
# Uses connect method to simplify setting up connections

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
workflow.connect('input', 'rev.input')
# workflow.reverse_sort -> sort_step.reverse
workflow.connect('reverse_sort', 'sorted.reverse')
# rev_step.output -> sort_step.input
workflow.connect('rev.output', 'sorted.input')
# sort_step.output -> workflow.output
workflow.connect('sorted.output', 'output')

print(yaml.safe_dump(workflow.save(), default_flow_style=False))
