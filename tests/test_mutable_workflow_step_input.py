from unittest import TestCase

from cwlpy import WorkflowStepInput, ValidationException


class WorkflowStepInputTestCase(TestCase):

    def setUp(self):
        self.step_input = WorkflowStepInput('my-step-input')

    def test_id(self):
        self.assertEqual(self.step_input.id, 'my-step-input')

    def test_save(self):
        saved = self.step_input.save()
        self.assertEqual(saved['id'], 'my-step-input')

    def test_set_source_string(self):
        self.step_input.set_source('step1/output')
        self.assertEqual(self.step_input.source, 'step1/output')

    def test_set_source_list(self):
        source_list = ['step1/output','step2/output']
        self.step_input.set_source(source_list)
        self.assertEqual(self.step_input.source, source_list)

    def test_validates_source(self):
        with self.assertRaises(ValidationException):
            self.step_input.set_source({})

    def test_validates_source_list(self):
        with self.assertRaises(ValidationException):
            self.step_input.set_source([1,2,3])
