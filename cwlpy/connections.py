import cwl_schema
from cwlpy.exceptions import ValidationException
from cwlpy.parameters import InputParameter, WorkflowOutputParameter
from cwlpy.step import WorkflowStepInput, WorkflowStepOutput


class WorkflowStepConnectionBase(object):

    # TODO: Verify input and output data types when connecting
    # It's possible (and likely) that "run" will be file name
    # and not a fully-formed object. But we can easily load that
    # file and inspect its inputs/outputs/data types when connecting.

    def __init__(self, workflow, steps):
        if not isinstance(workflow, cwl_schema.Workflow):
            raise ValidationException("workflow is not a Workflow")
        for step in steps:
            if not isinstance(step, cwl_schema.WorkflowStep):
                raise ValidationException("step is not a WorkflowStep")
            if step not in workflow.steps:
                raise ValidationException("step is not a part of workflow")
        self.workflow = workflow
        self.steps = steps


class WorkflowInputConnection(WorkflowStepConnectionBase):

    def _connect_workflow_single_input(self, workflow_input_id, step_input_id, step):
        # If workflow has an input parameter, get it
        input_parameter = self.workflow.input_parameter_by_id(workflow_input_id)
        if not input_parameter:
            input_parameter = InputParameter(workflow_input_id)
            self.workflow.add_input_parameter(input_parameter)
        workflow_step_input = WorkflowStepInput(step_input_id)
        # Now connect them
        workflow_step_input.source = input_parameter
        # This verifies the step is not already connected
        step.add_input(workflow_step_input)

    def connect(self, workflow_input_id, step_input_ids):
        """
        Connects a workflow input to step inputs
        """
        # The workflow input may be connected more than once
        # but the step input should only be connected once
        if len(step_input_ids) != len(self.steps):
            raise ValidationException("step_input_ids len does not match steps len")
        for index, step in enumerate(self.steps):
            step_input_id = step_input_ids[index]
            self._connect_workflow_single_input(workflow_input_id, step_input_id, step)


class WorkflowStepConnection(WorkflowStepConnectionBase):

    def connect(self, step_output_id, step_input_id):
        # Simple case, connecting 1:1 output->input
        if not len(self.steps) == 2:
            raise ValidationException("Can only connect with two steps")
        output_step, input_step = self.steps
        workflow_step_output = output_step.workflow_step_output_by_id(step_output_id)
        if not workflow_step_output:
            workflow_step_output = WorkflowStepOutput(step_output_id)
            output_step.add_output(workflow_step_output)
        workflow_step_input = WorkflowStepInput(step_input_id)
        source = '{}/{}'.format(output_step.id, step_output_id)
        workflow_step_input.set_source(source)
        input_step.add_input(workflow_step_input)  # Should raise if already connected


class WorkflowOutputConnection(WorkflowStepConnectionBase):

    def _connect_workflow_single_output(self, workflow_output_id, step_output_id, step):
        # If step has an output, get it
        workflow_step_output = step.workflow_step_output_by_id(step_output_id)
        if not workflow_step_output:
            workflow_step_output = WorkflowStepOutput(step_output_id)
            step.add_output(workflow_step_output)
        # Check existing output parameters
        output_parameters = [output for output in self.workflow.outputs if output.id == workflow_output_id]
        for output_parameter in output_parameters:
            if output_parameter.outputSource:
                raise ValidationException('Output parameter exists and is already connected')
        if not output_parameters:
            output_parameters = [WorkflowOutputParameter(workflow_output_id)]

        output_source = '{}/{}'.format(step.id, step_output_id)
        for output_parameter in output_parameters:
            output_parameter.set_outputSource(output_source)
            self.workflow.add_output_parameter(output_parameter)

    def connect(self, step_output_id, workflow_output_ids):
        """
        Connect's a workflow's output to a step's output
        """
        # A step output may be connected to multiple workflow outputs
        # But for now (until sink is implemented), mutliple steps may not be connected to a single workflow output
        if len(self.steps) != 1:
            raise ValidationException("Cannot connect multiple steps to a single workflow output")
        for workflow_output_id in workflow_output_ids:
            self._connect_workflow_single_output(workflow_output_id, step_output_id, self.steps[0])
