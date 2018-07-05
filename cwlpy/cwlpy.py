import os
import six
import cwl_schema

CWL_VERSION_STRING = 'v1.0'
LOADING_OPTIONS = cwl_schema.LoadingOptions()
BASE_URI = cwl_schema.file_uri(os.getcwd())


class ValidationException(cwl_schema.ValidationException):
    pass


class TemplateDocs(object):
    # These should probably be factories
    Workflow = {
        'class': 'Workflow',
        'cwlVersion': CWL_VERSION_STRING,
        'inputs': [],
        'outputs': [],
        'steps': [],
    }

    WorkflowStep = {
        'id': '',
        'in': [],
        'out': [],
        'run': '',
    }

    WorkflowStepInput = {
        'id': '',
    }

    WorkflowStepOutput = {
        'id': '',
    }

    InputParameter = {
        'id': '',
    }

    WorkflowOutputParameter = {
        'id': '',
    }


class Workflow(cwl_schema.Workflow):

    def __init__(self, id):
        super(Workflow, self).__init__(dict(TemplateDocs.Workflow), id, LOADING_OPTIONS)
        self.id = id

    def add_step(self, step):
        # Must be a step!
        if not isinstance(step, cwl_schema.WorkflowStep):
            raise ValidationException("Not a WorkflowStep")
        self.steps.append(step)

    def input_parameter_by_id(self, id):
        for param in self.inputs:
            if param.id == id:
                return param
        return None

    def add_input_parameter(self, input_parameter):
        if not isinstance(input_parameter, cwl_schema.InputParameter):
            raise ValidationException("Not an InputParameter")
        self.inputs.append(input_parameter)

    def add_output_parameter(self, output_parameter):
        if not isinstance(output_parameter, cwl_schema.WorkflowOutputParameter):
            raise ValidationException("Not an WorkflowOutputParameter")
        self.outputs.append(output_parameter)


class WorkflowStep(cwl_schema.WorkflowStep):

    def __init__(self, id):
        super(WorkflowStep, self).__init__(TemplateDocs.WorkflowStep, id, LOADING_OPTIONS)

    def add_input(self, step_input):
        if not isinstance(step_input, cwl_schema.WorkflowStepInput):
            raise ValidationException("Not a WorkflowStepInput")
        input_ids = [i.id for i in self.in_]
        if step_input.id in input_ids:
            raise ValidationException("Step already has input with id: " + step_input.id)
        self.in_.append(step_input)

    def add_output(self, step_output):
        if not isinstance(step_output, cwl_schema.WorkflowStepOutput):
            raise ValidationException("Not a WorkflowStepOutput")
        output_ids = [o.id for o in self.out]
        if step_output.id in output_ids:
            raise ValidationException("Step already has output with id: " + step_output.id)
        self.out.append(step_output)

    def set_run(self, run):
        # Would like this to be a @property, but that's awkward with the codegen
        allowed_types = [six.string_types, cwl_schema.CommandLineTool, cwl_schema.ExpressionTool, cwl_schema.Workflow]
        if not any([isinstance(run, allowed) for allowed in allowed_types]):
            raise ValidationException("Not an allowed type")
        self.run = run

    def workflow_step_output_by_id(self, id):
        for workflow_step_output in self.out:
            if workflow_step_output.id == id:
                return workflow_step_output
        return None


class WorkflowStepInput(cwl_schema.WorkflowStepInput):

    def __init__(self, id):
        super(WorkflowStepInput, self).__init__(TemplateDocs.WorkflowStepInput, id, LOADING_OPTIONS)

    @staticmethod
    def _is_list_of_strings(source_list):
        if isinstance(source_list, list):
            return all([isinstance(source, six.string_types) for source in source_list ])
        else:
            return False

    def set_source(self, source):
        # Validate that it's a string or a list of strings
        if not self._is_list_of_strings(source) and not isinstance(source, six.string_types):
            raise ValidationException("Source must be a string or array of strings")
        # TODO: Inspect the link and make sure the type is valid
        self.source = source


class WorkflowStepOutput(cwl_schema.WorkflowStepOutput):

    def __init__(self, id):
        super(WorkflowStepOutput, self).__init__(TemplateDocs.WorkflowStepOutput, id, LOADING_OPTIONS)


class InputParameter(cwl_schema.InputParameter):

    def __init__(self, id):
        super(InputParameter, self).__init__(TemplateDocs.InputParameter, id, LOADING_OPTIONS)


class WorkflowOutputParameter(cwl_schema.WorkflowOutputParameter):

    def __init__(self, id):
        super(WorkflowOutputParameter, self).__init__(TemplateDocs.WorkflowOutputParameter, id, LOADING_OPTIONS)

    def set_outputSource(self, outputSource):
        if not isinstance(outputSource, six.string_types):
            # TODO: Also check for array of strings, since it's a sink type
            # TODO: Inspect the link and make sure the type is valid
            raise ValidationException("outputSource should be a string")
        self.outputSource = outputSource


class WorkflowStepConnection(object):

    # TODO: Verify input and output data types when connecting
    # It's possible (and likely) that "run" will be file name
    # and not a fully-formed object. But we can easily load that
    # file and inspect its inputs/outputs/data types when connecting.

    def __init__(self, workflow, steps):
        for step in steps:
            if not isinstance(step, cwl_schema.WorkflowStep):
                raise ValidationException("step is not a WorkflowStep")
            if step not in workflow.steps:
                raise ValidationException("step is not a part of workflow")
        if not isinstance(workflow, cwl_schema.Workflow):
            raise ValidationException("workflow is not a Workflow")
        self.workflow = workflow
        self.steps = steps

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

    def connect_workflow_input(self, workflow_input_id, step_input_ids):
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

    def _connect_workflow_single_output(self, workflow_output_id, step_output_id, step):
        # If step has an output, get it
        workflow_step_output = step.workflow_step_output_by_id(step_output_id)
        if not workflow_step_output:
            workflow_step_output = WorkflowStepOutput(step_output_id)
            step.add_output(workflow_step_output)
        # Instantiate a workflow output
        output_parameter = WorkflowOutputParameter(workflow_output_id)
        # Now connect them
        output_source = '{}/{}'.format(step.id, step_output_id)
        output_parameter.set_outputSource(output_source)
        self.workflow.add_output_parameter(output_parameter)

    def connect_workflow_output(self, workflow_output_id, step_output_ids):
        """
        Connect's a workflow's output to a step's output
        """
        # The step output may be connected more than once
        # but the workflow output should only be connected once
        if len(step_output_ids) != len(self.steps):
            raise ValidationException("step_output_ids len does not match steps len")
        for index, step in enumerate(self.steps):
            step_output_id = step_output_ids[index]
            self._connect_workflow_single_output(workflow_output_id, step_output_id, step)

    def connect_step_output_input(self, step_output_id, step_input_id):
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
