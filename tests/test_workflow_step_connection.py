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
        with self.assertRaises(ValidationException) as cm:
            WorkflowStepConnection(self.workflow, [step])
        self.assertIn('not a part of workflow', repr(cm.exception))

    def test_fails_if_not_a_workflow(self):
        with self.assertRaises(ValidationException) as cm:
            WorkflowStepConnection({}, self.steps)
        self.assertIn('not a Workflow', repr(cm.exception))

    def test_fails_if_steps_not_steps(self):
        with self.assertRaises(ValidationException) as cm:
            WorkflowStepConnection(self.workflow, [1,2,3])
        self.assertIn('not a WorkflowStep', repr(cm.exception))


class WorkflowStepConnectionInputTestCase(WorkflowStepConnectionBase):

    def setUp(self):
        super(WorkflowStepConnectionInputTestCase, self).setUp()
        self.connection = WorkflowStepConnection(self.workflow, self.steps)

    def test_connects_workflow_input_to_step_inputs(self):
        workflow_input_id = 'workflow-input-1'
        step_input_ids = ['step-1-input-1', 'step-2-input-1']
        self.connection.connect_workflow_input(workflow_input_id, step_input_ids)
        # Step should have input connected to workflow
        saved = self.workflow.save()
        # Source of first step's first input is the workflow input id
        self.assertEqual(saved['steps'][0]['in'][0]['source']['id'], 'workflow-input-1')
        # Source of second step's input is also the workflow input id
        self.assertEqual(saved['steps'][1]['in'][0]['source']['id'], 'workflow-input-1')

    def test_validates_length_of_input_ids(self):
        step_inputs = ['step1-input1','step1-input2','step1-input3']
        self.assertNotEqual(len(step_inputs), len(self.steps))
        with self.assertRaises(ValidationException) as cm:
            self.connection.connect_workflow_input('workflow-input', step_inputs)
        self.assertIn('len does not match', repr(cm.exception))

    def test_reuses_workflow_input_parameter_by_id(self):
        self.assertEqual(len(self.workflow.inputs), 0)
        # When making two connections to a single workflow input, the workflow should have input
        workflow_input_id = 'workflow-input-1'
        step_input_ids = ['step-1-input-1', 'step-2-input-1']
        self.connection.connect_workflow_input(workflow_input_id, step_input_ids)
        self.assertEqual(len(self.workflow.inputs), 1)

    def test_connects_multiple_inputs_single_step(self):
        workflow = Workflow('workflow')
        step = WorkflowStep('step')
        workflow.add_step(step)
        connection = WorkflowStepConnection(workflow, [step])
        connection.connect_workflow_input('workflow-input-1', ['step-input-1'])
        connection.connect_workflow_input('workflow-input-2', ['step-input-2'])
        saved = workflow.save()
        step_inputs = saved['steps'][0]['in']
        self.assertEqual(step_inputs[0]['source']['id'], 'workflow-input-1')
        self.assertEqual(step_inputs[0]['id'], 'step-input-1')
        self.assertEqual(step_inputs[1]['source']['id'], 'workflow-input-2')
        self.assertEqual(step_inputs[1]['id'], 'step-input-2')

    def test_fails_if_step_already_connected(self):
        workflow = Workflow('workflow')
        step = WorkflowStep('step')
        workflow.add_step(step)
        connection = WorkflowStepConnection(workflow, [step])
        connection.connect_workflow_input('workflow-input-1', ['step-input-1'])
        connection.connect_workflow_input('workflow-input-2', ['step-input-2'])
        with self.assertRaises(ValidationException) as cm:
            connection.connect_workflow_input('workflow-input-3', ['step-input-1'])
        self.assertIn('Step already has input with id: step-input-1', repr(cm.exception))

