from unittest import TestCase
from cwlpy import MutableWorkflow, MutableInputParameter, MutableWorkflowOutputParameter, ValidationException

class MutableWorkflowTestCase(TestCase):

    def setUp(self):
        self.workflow = MutableWorkflow('my-workflow')

    def test_id(self):
        self.assertEqual(self.workflow.id, 'my-workflow')

    def test_save(self):
        saved = self.workflow.save()
        self.assertEqual(saved['class'], 'Workflow')
        self.assertEqual(saved['id'], 'my-workflow')

    def test_validates_add_step(self):
        with self.assertRaises(ValidationException):
            self.workflow.add_step('not-a-workflowstep')

    def test_add_input_parameter(self):
        input_parameter = MutableInputParameter('input-1')
        self.workflow.add_input_parameter(input_parameter)
        self.assertIn(input_parameter, self.workflow.inputs)

    def test_validates_add_input_parameter_type(self):
        with self.assertRaises(ValidationException):
            self.workflow.add_input_parameter('not-input-parameter')

    def test_finds_input_parameter_by_id(self):
        input_parameter = MutableInputParameter('input-2')
        self.workflow.add_input_parameter(input_parameter)
        self.assertEqual(input_parameter, self.workflow.input_parameter_by_id('input-2'))
        self.assertIsNone(self.workflow.input_parameter_by_id('foobar'))

    def test_add_output_parameter(self):
        output_parameter = MutableWorkflowOutputParameter('output-1')
        self.workflow.add_output_parameter(output_parameter)
        self.assertIn(output_parameter, self.workflow.outputs)

    def test_validates_add_output_parameter(self):
        with self.assertRaises(ValidationException):
            self.workflow.add_output_parameter('not-output-parameter')
