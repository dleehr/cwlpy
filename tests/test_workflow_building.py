from unittest import TestCase

from cwlpy import Workflow, WorkflowStep as Step
from ruamel import yaml


REVSORT_WORKFLOW = """class: Workflow
cwlVersion: v1.0
id: revsort
inputs:
- id: wf-input
- id: wf-reverse_sort
outputs:
- id: wf-output
  outputSource: sorted/sortstep-output
steps:
- id: rev
  in:
  - id: revstep-input
    source:
      id: wf-input
  out:
  - id: revstep-output
  run: revtool.cwl
- id: sorted
  in:
  - id: sortstep-reverse
    source:
      id: wf-reverse_sort
  - id: sortstep-input
    source: rev/revstep-output
  out:
  - id: sortstep-output
  run: sorttool.cwl
"""


class WorkflowBuilderTestCase(TestCase):

    def test_building_revsort(self):

        workflow = Workflow('revsort')
        rev_step = Step('rev', run='revtool.cwl')
        sort_step = Step('sorted', run='sorttool.cwl')

        # Add steps by chaining
        workflow.step(rev_step).step(sort_step)

        ########################################
        # Connect workflow and steps
        ########################################

        # workflow.input -> rev_step.input, workflow.reverse_sort -> sort_step.output
        workflow.\
            connect_input(rev_step, 'wf-input', 'revstep-input').\
            connect_input(sort_step, 'wf-reverse_sort', 'sortstep-reverse')

        # rev_step.output -> sort_step.input
        workflow.connect_steps(rev_step, sort_step, 'revstep-output', 'sortstep-input')

        # sort_step.output -> workflow.output
        workflow.connect_output(sort_step, 'sortstep-output', 'wf-output')

        yaml_string = yaml.safe_dump(workflow.save(), default_flow_style=False)
        self.assertMultiLineEqual(REVSORT_WORKFLOW, str(yaml_string))
