from unittest import TestCase

from cwlpy import WorkflowInputConnection, WorkflowStepConnection, WorkflowOutputConnection, \
    ValidationException, Workflow, WorkflowStep


class WorkflowStepConnectionCommonTests(object):

    def setUp(self):
        self.test_cls = None
        self.workflow = Workflow('workflow-1')
        self.steps = [WorkflowStep('step-1'), WorkflowStep('step-2')]
        [self.workflow.add_step(step) for step in self.steps]

    def test_initializes_successfully(self):
        connection = self.test_cls(self.workflow, self.steps)
        self.assertIsNotNone(connection)
        self.assertEqual(connection.workflow, self.workflow)
        self.assertEqual(connection.steps, self.steps)

    def test_fails_if_steps_not_part_of_workflow(self):
        step = WorkflowStep('step-3')
        self.assertNotIn(step, self.workflow.steps)
        with self.assertRaises(ValidationException) as cm:
            self.test_cls(self.workflow, [step])
        self.assertIn('not a part of workflow', repr(cm.exception))

    def test_fails_if_not_a_workflow(self):
        with self.assertRaises(ValidationException) as cm:
            self.test_cls({}, self.steps)
        self.assertIn('not a Workflow', repr(cm.exception))

    def test_fails_if_steps_not_steps(self):
        with self.assertRaises(ValidationException) as cm:
            self.test_cls(self.workflow, [1, 2, 3])
        self.assertIn('not a WorkflowStep', repr(cm.exception))


class WorkflowInputConnectionTestCase(WorkflowStepConnectionCommonTests, TestCase):

    def setUp(self):
        super(WorkflowInputConnectionTestCase, self).setUp()
        self.test_cls = WorkflowInputConnection
        self.connection = WorkflowInputConnection(self.workflow, self.steps)

    def test_connects_workflow_input_to_step_inputs(self):
        workflow_input_id = 'workflow-input-1'
        step_input_ids = ['step-1-input-1', 'step-2-input-1']
        self.connection.connect(workflow_input_id, step_input_ids)
        # Step should have input connected to workflow
        saved = self.workflow.save()
        # Source of first step's first input is the workflow input id
        self.assertEqual(saved['steps'][0]['in'][0]['source']['id'], 'workflow-input-1')
        # Source of second step's input is also the workflow input id
        self.assertEqual(saved['steps'][1]['in'][0]['source']['id'], 'workflow-input-1')

    def test_validates_length_of_input_ids(self):
        step_inputs = ['step1-input1', 'step1-input2', 'step1-input3']
        self.assertNotEqual(len(step_inputs), len(self.steps))
        with self.assertRaises(ValidationException) as cm:
            self.connection.connect('workflow-input', step_inputs)
        self.assertIn('len does not match', repr(cm.exception))

    def test_reuses_workflow_input_parameter_by_id(self):
        self.assertEqual(len(self.workflow.inputs), 0)
        # When making two connections to a single workflow input, the workflow should have input
        workflow_input_id = 'workflow-input-1'
        step_input_ids = ['step-1-input-1', 'step-2-input-1']
        self.connection.connect(workflow_input_id, step_input_ids)
        self.assertEqual(len(self.workflow.inputs), 1)

    def test_connects_multiple_inputs_single_step(self):
        workflow = Workflow('workflow')
        step = WorkflowStep('step')
        workflow.add_step(step)
        connection = WorkflowInputConnection(workflow, [step])
        connection.connect('workflow-input-1', ['step-input-1'])
        connection.connect('workflow-input-2', ['step-input-2'])
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
        connection = WorkflowInputConnection(workflow, [step])
        connection.connect('workflow-input-1', ['step-input-1'])
        connection.connect('workflow-input-2', ['step-input-2'])
        with self.assertRaises(ValidationException) as cm:
            connection.connect('workflow-input-3', ['step-input-1'])
        self.assertIn('Step already has input with id: step-input-1', repr(cm.exception))


class WorkflowOutputConnectionTestCase(WorkflowStepConnectionCommonTests, TestCase):

    def setUp(self):
        super(WorkflowOutputConnectionTestCase, self).setUp()
        self.test_cls = WorkflowOutputConnection
        # Just connecting the last step
        self.connection = WorkflowOutputConnection(self.workflow, self.steps[1:2])

    def test_fails_when_connecting_output_to_multiple_steps(self):
        self.assertEqual(len(self.steps), 2)
        connection = WorkflowOutputConnection(self.workflow, self.steps)
        with self.assertRaises(ValidationException) as cm:
            connection.connect('s1', ['w1'])
        self.assertIn('Cannot connect multiple steps', repr(cm.exception))

    def test_connects_workflow_outputs_to_step_output(self):
        workflow_output_ids = ['workflow-output-1', 'workflow-output-2']
        step_output_id = 'step-2-output-1'
        self.connection.connect(step_output_id, workflow_output_ids)
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
        self.connection.connect(step_output_id, ['workflow-output-1'])
        self.connection.connect(step_output_id, ['workflow-output-2'])
        self.assertEqual(len(self.workflow.steps[1].out), 1)
        self.assertEqual(len(self.workflow.outputs), 2)

    def test_fails_if_workflow_output_already_connected(self):
        workflow_output_ids = ['workflow-output-1']
        # Connecting another step to the same workflow output should fail.
        self.connection.connect('step-2-output-1', workflow_output_ids)
        with self.assertRaises(ValidationException) as cm:
            self.connection.connect('step-2-output-2', workflow_output_ids)
        self.assertIn('Output parameter exists and is already connected', repr(cm.exception))


class WorkflowStepConnectionTestCase(WorkflowStepConnectionCommonTests, TestCase):

    def setUp(self):
        super(WorkflowStepConnectionTestCase, self).setUp()
        self.test_cls = WorkflowStepConnection
        # Step output -> input connections require exactly two steps
        self.connection = WorkflowStepConnection(self.workflow, self.steps)

    def test_requires_two_steps(self):
        single_step = self.steps[0:1]
        self.assertEqual(len(single_step), 1)
        connection1 = WorkflowStepConnection(self.workflow, single_step)
        with self.assertRaises(ValidationException) as cm:
            connection1.connect('O', 'I')
        self.assertIn('Can only connect with two steps', repr(cm.exception))
        four_steps = self.steps + self.steps
        self.assertEqual(len(four_steps), 4)
        connection4 = WorkflowStepConnection(self.workflow, four_steps)
        with self.assertRaises(ValidationException) as cm:
            connection4.connect('O', 'I')
        self.assertIn('Can only connect with two steps', repr(cm.exception))

    def test_connects_step_output_to_input(self):
        self.connection.connect('step-1-output', 'step-2-input')
        saved = self.workflow.save()
        step_1_outputs = saved['steps'][0]['out']
        step_2_inputs = saved['steps'][1]['in']
        self.assertEqual(step_1_outputs[0]['id'], 'step-1-output')
        self.assertEqual(step_2_inputs[0]['id'], 'step-2-input')
        self.assertEqual(step_2_inputs[0]['source'], 'step-1/step-1-output')

    def test_reuses_workflow_step_output_by_id(self):
        self.assertEqual(len(self.workflow.steps[0].out), 0)
        self.assertEqual(len(self.workflow.steps[1].in_), 0)
        self.connection.connect('step-1-output', 'step-2-input-1')
        self.connection.connect('step-1-output', 'step-2-input-2')
        # Connecting output of step 1 to two inputs on step 2 should result in one output and two inputs
        self.assertEqual(len(self.workflow.steps[0].out), 1)
        self.assertEqual(len(self.workflow.steps[1].in_), 2)

    def test_fails_if_input_already_connected(self):
        self.connection.connect('step-1-output-1', 'step-2-input')
        with self.assertRaises(ValidationException) as cm:
            self.connection.connect('step-1-output-2', 'step-2-input')
        self.assertIn('Step already has input', repr(cm.exception))
