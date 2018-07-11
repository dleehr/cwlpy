import six
import inspect
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


# This package provides methods to build up CWL documents backed by auto-generated classes
# Since those auto-generated classes may be instantiated elsewhere (e.g. load_document),
# we add methods to the classes here, so that objects loaded from CWL documents can be edited
# using the python functionality here

def add_methods(source_cls, dest_cls):
    for m in inspect.getmembers(source_cls, predicate=inspect.isfunction):
        setattr(dest_cls, m[0], m[1])




