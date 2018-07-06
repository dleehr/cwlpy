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


class WorkflowStepConnectionOutputTestCase(WorkflowStepConnectionBase):

    def setUp(self):
        super(WorkflowStepConnectionOutputTestCase, self).setUp()
        # Just connecting the last step
        self.connection = WorkflowStepConnection(self.workflow, self.steps[1:2])

    def test_fails_when_connecting_output_to_multiple_steps(self):
        self.assertEqual(len(self.steps), 2)
        connection = WorkflowStepConnection(self.workflow, self.steps)
        with self.assertRaises(ValidationException) as cm:
            connection.connect_workflow_output(['w1'], 's1')
        self.assertIn('Cannot connect multiple steps', repr(cm.exception))

    def test_connects_workflow_outputs_to_step_output(self):
        workflow_output_ids = ['workflow-output-1', 'workflow-output-2']
        step_output_id = 'step-2-output-1'
        self.connection.connect_workflow_output(workflow_output_ids, step_output_id)
        # Step should have input connected to workflow
        saved = self.workflow.save()
        workflow_outputs = saved['outputs']
        # We're connecting two workflow outputs to output-1 of step-2
        self.assertEqual(workflow_outputs[0]['outputSource'], 'step-2/step-2-output-1')
        self.assertEqual(workflow_outputs[0]['id'], 'workflow-output-1')
        self.assertEqual(workflow_outputs[1]['outputSource'], 'step-2/step-2-output-1')
        self.assertEqual(workflow_outputs[1]['id'], 'workflow-output-2')

    def test_reuses_workflow_step_output_by_id(self):
        # Connect 1 step's output to two workflow outputs
        # Verify that two workflow outputs are created and the step only has one output
        self.assertEqual(len(self.workflow.steps[1].out), 0)
        self.assertEqual(len(self.workflow.outputs), 0)
        step_output_id = 'step-2-output-1'
        self.connection.connect_workflow_output(['workflow-output-1'], step_output_id)
        self.connection.connect_workflow_output(['workflow-output-2'], step_output_id)
        self.assertEqual(len(self.workflow.steps[1].out), 1)
        self.assertEqual(len(self.workflow.outputs), 2)

    def test_fails_if_workflow_output_already_connected(self):
        workflow_output_ids = ['workflow-output-1']
        # Connecting another step to the same workflow output should fail.
        self.connection.connect_workflow_output(workflow_output_ids, 'step-2-output-1')
        with self.assertRaises(ValidationException) as cm:
            self.connection.connect_workflow_output(workflow_output_ids, 'step-2-output-2')
        self.assertIn('Output parameter exists and is already connected', repr(cm.exception))
