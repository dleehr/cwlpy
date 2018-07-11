import cwl_schema
import six
from cwlpy.exceptions import ValidationException
from cwlpy.utils import is_list_of_strings, add_methods, TemplateDocs, LOADING_OPTIONS


class _WorkflowStep(object):

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


class _WorkflowStepInput(object):

    def set_source(self, source):
        # Validate that it's a string or a list of strings
        if not is_list_of_strings(source) and not isinstance(source, six.string_types):
            raise ValidationException("Source must be a string or array of strings")
        # TODO: Inspect the link and make sure the type is valid
        self.source = source


add_methods(_WorkflowStep, cwl_schema.WorkflowStep)
add_methods(_WorkflowStepInput, cwl_schema.WorkflowStepInput)

class WorkflowStep(cwl_schema.WorkflowStep):

    def __init__(self, id, run=None):
        super(WorkflowStep, self).__init__(TemplateDocs.WorkflowStep, id, LOADING_OPTIONS)
        if run:
            self.set_run(run)


class WorkflowStepInput(cwl_schema.WorkflowStepInput):

    def __init__(self, id):
        super(WorkflowStepInput, self).__init__(TemplateDocs.WorkflowStepInput, id, LOADING_OPTIONS)


class WorkflowStepOutput(cwl_schema.WorkflowStepOutput):

    def __init__(self, id):
        super(WorkflowStepOutput, self).__init__(TemplateDocs.WorkflowStepOutput, id, LOADING_OPTIONS)

