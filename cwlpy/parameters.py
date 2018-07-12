from __future__ import absolute_import

import six

import cwl_schema
from cwlpy.exceptions import ValidationException
from cwlpy.utils import is_list_of_strings, TemplateDocs, LOADING_OPTIONS


def set_outputSource(self, outputSource):
    if not is_list_of_strings(outputSource) and not isinstance(outputSource, six.string_types):
        raise ValidationException("outputSource must be a string or array of strings")
    # TODO: Inspect the link and make sure the type is valid
    self.outputSource = outputSource


cwl_schema.WorkflowOutputParameter.set_outputSource = set_outputSource


class WorkflowOutputParameter(cwl_schema.WorkflowOutputParameter):

    def __init__(self, id):
        super(WorkflowOutputParameter, self).__init__(TemplateDocs.WorkflowOutputParameter, id, LOADING_OPTIONS)


class InputParameter(cwl_schema.InputParameter):

    def __init__(self, id):
        super(InputParameter, self).__init__(TemplateDocs.InputParameter, id, LOADING_OPTIONS)
