from cwlpy import *
import pprint

workflow = Workflow('myworkflow')
step1 = WorkflowStep('step1')
step1.set_run('step1-tool.cwl')
step2 = WorkflowStep('step2')
step2.set_run('step2-tool.cwl')
workflow.add_step(step1)
workflow.add_step(step2)
connection1 = WorkflowStepConnection(workflow, [step1, step2])
connection1.connect_workflow_input('workflow-input', ['step-input1','step-input2'])
connection2 = WorkflowStepConnection(workflow, [step2])
connection2.connect_workflow_output('workflow-output', ['step2-output'])
# Now make an internal connection
connection1.connect_step_output_input('step1-output','step2-input')
pprint.pprint(workflow.save())

