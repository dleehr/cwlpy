from unittest import TestCase

from cwlpy import WorkflowStepOutput


class WorkflowStepOutputTestCase(TestCase):

    def setUp(self):
        self.step_output = WorkflowStepOutput('my-step-output')

    def test_id(self):
        self.assertEqual(self.step_output.id, 'my-step-output')

    def test_save(self):
        saved = self.step_output.save()
        self.assertEqual(saved['id'], 'my-step-output')

