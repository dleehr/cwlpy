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
workflow.connect_input(rev_step).connect('input',['input'])
# workflow.reverse_sort -> sort_step.output
workflow.connect_input(sort_step).connect('reverse_sort', ['reverse'])
# rev_step.output -> sort_step.input
workflow.connect_steps(rev_step, sort_step).connect('output','input')
# sort_step.output -> workflow.output
workflow.connect_output(sort_step).connect('step-output', ['wf-output'])

print(yaml.safe_dump(workflow.save(), default_flow_style=False))
