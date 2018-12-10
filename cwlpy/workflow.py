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


def find_step_by_id(self, step_id):
    for step in self.steps:
        if step.id == step_id:
            return step
    raise ValidationException("Step id not found: {}".format(step_id))


def connect(self, source, dest):
    """
    Connects workflow_inputs/step_outputs to step_inputs/workflow_outputs.
    Calls appropriate method (connect_steps, connect_output, or connect_input) based on source and dest.
    Raises ValidationException if user tries to connect workflow input to workflow output.
    :param self: Workflow
    :param source: str: if contains a '.' is a step output name otherwise it is a workflow input
    :param dest: str: if contains a '.' is a step input name otherwise it is a workflow output
    """
    source_is_from_step = '.' in source
    dest_is_to_step = '.' in dest
    if source_is_from_step:
        source_step_id, source_id = source.split('.')
        source_step = find_step_by_id(self, source_step_id)
        if dest_is_to_step:
            dest_step_id, dest_id = dest.split('.')
            dest_step = find_step_by_id(self, dest_step_id)
            self.connect_steps(source_step, dest_step, source_id, dest_id)
        else:
            self.connect_output(source_step, dest, workflow_output_id=source_id)
    else:
        if dest_is_to_step:
            dest_step_id, dest_id = dest.split('.')
            dest_step = find_step_by_id(self, dest_step_id)
            self.connect_input(dest_step, source, dest_id)
        else:
            raise ValidationException("Cannot connect input to output source: {} dest: {}".format(source, dest))


cwl_schema.Workflow.add_step = add_step
cwl_schema.Workflow.step = step
cwl_schema.Workflow.input_parameter_by_id = input_parameter_by_id
cwl_schema.Workflow.add_input_parameter = add_input_parameter
cwl_schema.Workflow.add_output_parameter = add_output_parameter
cwl_schema.Workflow.connect_input = connect_input
cwl_schema.Workflow.connect_output = connect_output
cwl_schema.Workflow.connect_steps = connect_steps
cwl_schema.Workflow.connect = connect
cwl_schema.Workflow.find_step_by_id = find_step_by_id


class Workflow(cwl_schema.Workflow):

    def __init__(self, id):
        super(Workflow, self).__init__(dict(TemplateDocs.Workflow), id, LOADING_OPTIONS)
        self.id = id
