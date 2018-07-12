from __future__ import absolute_import

import cwl_schema
from cwlpy.connections import WorkflowInputConnection, WorkflowOutputConnection, WorkflowStepConnection
from cwlpy.exceptions import ValidationException
from cwlpy.utils import TemplateDocs, LOADING_OPTIONS


def add_step(self, step):
    # Must be a step!
    if not isinstance(step, cwl_schema.WorkflowStep):
        raise ValidationException("Not a WorkflowStep")
    self.steps.append(step)


def step(self, step):
    self.add_step(step)
    return self


def input_parameter_by_id(self, id):
    for param in self.inputs:
        if param.id == id:
            return param
    return None


def add_input_parameter(self, input_parameter):
    if not isinstance(input_parameter, cwl_schema.InputParameter):
        raise ValidationException("Not an InputParameter")
    self.inputs.append(input_parameter)
    return self


def add_output_parameter(self, output_parameter):
    if not isinstance(output_parameter, cwl_schema.WorkflowOutputParameter):
        raise ValidationException("Not a WorkflowOutputParameter")
    self.outputs.append(output_parameter)
    return self


def connect_input(self, step, workflow_input_id, step_input_id=None):
    connection = WorkflowInputConnection(self, [step])
    if step_input_id is None:
        step_input_id = workflow_input_id
    connection.connect(workflow_input_id, [step_input_id])
    return self


def connect_output(self, step, step_output_id, workflow_output_id=None):
    connection = WorkflowOutputConnection(self, [step])
    if workflow_output_id is None:
        workflow_output_id = step_output_id
    connection.connect(step_output_id, [workflow_output_id])
    return self


def connect_steps(self, output_step, input_step, step_output_id, step_input_id=None):
    connection = WorkflowStepConnection(self, [output_step, input_step])
    if step_input_id is None:
        step_input_id = step_output_id
    connection.connect(step_output_id, step_input_id)
    return self


cwl_schema.Workflow.add_step = add_step
cwl_schema.Workflow.step = step
cwl_schema.Workflow.input_parameter_by_id = input_parameter_by_id
cwl_schema.Workflow.add_input_parameter = add_input_parameter
cwl_schema.Workflow.add_output_parameter = add_output_parameter
cwl_schema.Workflow.connect_input = connect_input
cwl_schema.Workflow.connect_output = connect_output
cwl_schema.Workflow.connect_steps = connect_steps


class Workflow(cwl_schema.Workflow):

    def __init__(self, id):
        super(Workflow, self).__init__(dict(TemplateDocs.Workflow), id, LOADING_OPTIONS)
        self.id = id
