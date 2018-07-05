from unittest import TestCase

from cwlpy import WorkflowStepConnection, ValidationException, Workflow, WorkflowStep

class WorkflowStepConnectionBase(TestCase):

    def setUp(self):
        self.workflow = Workflow('workflow-1')
        self.steps = [WorkflowStep('step-1'), WorkflowStep('step-2')]
        [self.workflow.add_step(step) for step in self.steps]


class WorkflowStepConnectionInitializerTestCase(WorkflowStepConnectionBase):

    def test_initializes_successfully(self):
        connection = WorkflowStepConnection(self.workflow, self.steps)
        self.assertIsNotNone(connection)
        self.assertEqual(connection.workflow, self.workflow)
        self.assertEqual(connection.steps, self.steps)

    def test_fails_if_steps_not_part_of_workflow(self):
        step = WorkflowStep('step-3')
        self.assertNotIn(step, self.workflow.steps)
        with self.assertRaises(ValidationException):
            WorkflowStepConnection(self.workflow, [step])

    def test_fails_if_not_a_workflow(self):
        with self.assertRaises(ValidationException):
            WorkflowStepConnection({}, self.steps)

    def test_fails_if_steps_not_steps(self):
        with self.assertRaises(ValidationException):
            WorkflowStepConnection(self.workflow, [1,2,3])


