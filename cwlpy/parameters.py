import cwl_schema
import six
from cwlpy.exceptions import ValidationException
from cwlpy.utils import is_list_of_strings, add_methods, TemplateDocs, LOADING_OPTIONS


class _WorkflowOutputParameter(object):

    def set_outputSource(self, outputSource):
        if not is_list_of_strings(outputSource) and not isinstance(outputSource, six.string_types):
            raise ValidationException("outputSource must be a string or array of strings")
        # TODO: Inspect the link and make sure the type is valid
        self.outputSource = outputSource


add_methods(_WorkflowOutputParameter, cwl_schema.WorkflowOutputParameter)


class WorkflowOutputParameter(cwl_schema.WorkflowOutputParameter):

    def __init__(self, id):
        super(WorkflowOutputParameter, self).__init__(TemplateDocs.WorkflowOutputParameter, id, LOADING_OPTIONS)


class InputParameter(cwl_schema.InputParameter):

    def __init__(self, id):
        super(InputParameter, self).__init__(TemplateDocs.InputParameter, id, LOADING_OPTIONS)

