CWL_VERSION_STRING = 'v1.0'


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
