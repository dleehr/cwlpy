from unittest import TestCase

from cwlpy import WorkflowOutputParameter, ValidationException


class WorkflowOutputParameterTestCase(TestCase):

    def setUp(self):
        self.output_parameter = WorkflowOutputParameter('my-output-parameter')

    def test_id(self):
        self.assertEqual(self.output_parameter.id, 'my-output-parameter')

    def test_save(self):
        saved = self.output_parameter.save()
        self.assertEqual(saved['id'], 'my-output-parameter')

    def test_set_output_source_string(self):
        self.output_parameter.set_outputSource('step1/output')
        self.assertEqual(self.output_parameter.outputSource, 'step1/output')

    def test_set_output_source_list(self):
        source_list = ['step1/output','step2/output']
        self.output_parameter.set_outputSource(source_list)
        self.assertEqual(self.output_parameter.outputSource, source_list)

    def test_validates_output_source(self):
        with self.assertRaises(ValidationException) as cm:
            self.output_parameter.set_outputSource({})
        self.assertIn('outputSource must be', repr(cm.exception))

    def test_validates_output_source_list(self):
        with self.assertRaises(ValidationException) as cm:
            self.output_parameter.set_outputSource([1,2,3])
        self.assertIn('outputSource must be', repr(cm.exception))
