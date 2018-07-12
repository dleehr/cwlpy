import six
import cwl_schema
import os

CWL_VERSION_STRING = 'v1.0'
LOADING_OPTIONS = cwl_schema.LoadingOptions()
BASE_URI = cwl_schema.file_uri(os.getcwd())


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


def is_list_of_strings(source_list):
    if isinstance(source_list, list):
        return all([isinstance(source, six.string_types) for source in source_list])
    else:
        return False
