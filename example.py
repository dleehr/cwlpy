from cwlpy import *
from ruamel import yaml

# https://github.com/common-workflow-language/cwl-v1.1/blob/master/tests/revsort.cwl

########################################
# Create workflow and steps
########################################

workflow = Workflow('revsort')
rev_step = WorkflowStep('rev')
sort_step = WorkflowStep('sorted')

rev_step.set_run('revtool.cwl')
sort_step.set_run('sort.cwl')

workflow.add_step(rev_step)
workflow.add_step(sort_step)

########################################
# Connect workflow and steps
########################################

# workflow.input -> rev_step.input
WorkflowStepConnection(workflow, [rev_step]).connect_workflow_input('input', ['input'])
# workflow.reverse_sort -> sort_step.output
WorkflowStepConnection(workflow, [sort_step]).connect_workflow_input('reverse_sort', ['reverse'])
# rev_step.output -> sort_step.input
WorkflowStepConnection(workflow, [rev_step, sort_step]).connect_step_output_input('output','input')
# sort_step.output -> workflow.output
WorkflowStepConnection(workflow, [sort_step]).connect_workflow_output(['output'],'output')

print(yaml.safe_dump(workflow.save(), default_flow_style=False))
