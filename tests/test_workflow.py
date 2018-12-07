from unittest import TestCase
from mock import Mock

from cwlpy import Workflow, WorkflowStep, InputParameter, WorkflowOutputParameter, ValidationException


class WorkflowTestCase(TestCase):

    def setUp(self):
        self.workflow = Workflow('my-workflow')

    def test_id(self):
        self.assertEqual(self.workflow.id, 'my-workflow')

    def test_save(self):
        saved = self.workflow.save()
        self.assertEqual(saved['class'], 'Workflow')
        self.assertEqual(saved['id'], 'my-workflow')

    def test_validates_add_step(self):
        with self.assertRaises(ValidationException) as cm:
            self.workflow.add_step('not-a-workflowstep')
        self.assertIn('Not a WorkflowStep', repr(cm.exception))

    def test_add_input_parameter(self):
        input_parameter = InputParameter('input-1')
        self.workflow.add_input_parameter(input_parameter)
        self.assertIn(input_parameter, self.workflow.inputs)

    def test_validates_add_input_parameter_type(self):
        with self.assertRaises(ValidationException) as cm:
            self.workflow.add_input_parameter('not-input-parameter')
        self.assertIn('Not an InputParameter', repr(cm.exception))

    def test_finds_input_parameter_by_id(self):
        input_parameter = InputParameter('input-2')
        self.workflow.add_input_parameter(input_parameter)
        self.assertEqual(input_parameter, self.workflow.input_parameter_by_id('input-2'))
        self.assertIsNone(self.workflow.input_parameter_by_id('foobar'))

    def test_add_output_parameter(self):
        output_parameter = WorkflowOutputParameter('output-1')
        self.workflow.add_output_parameter(output_parameter)
        self.assertIn(output_parameter, self.workflow.outputs)

    def test_validates_add_output_parameter(self):
        with self.assertRaises(ValidationException) as cm:
            self.workflow.add_output_parameter('not-output-parameter')
        self.assertIn('Not a WorkflowOutputParameter', repr(cm.exception))


class WorkflowWithStepsTestCase(TestCase):

    def setUp(self):
        self.workflow = Workflow('my-workflow')
        self.step1  = WorkflowStep('my-step-1')
        self.step2 = WorkflowStep('my-step-2')

    def test_add_step(self):
        self.assertEqual(len(self.workflow.steps), 0)
        self.workflow.add_step(self.step1)
        self.assertEqual(len(self.workflow.steps), 1)
        self.assertIn(self.step1, self.workflow.steps)

    def test_step_convenience_method(self):
        self.assertEqual(len(self.workflow.steps), 0)
        retval = self.workflow.step(self.step2)
        self.assertEqual(len(self.workflow.steps), 1)
        self.assertIn(self.step2, self.workflow.steps)
        self.assertEqual(self.workflow, retval)

    def test_connect_input(self):
        self.workflow.add_step(self.step1)
        retval = self.workflow.connect_input(self.step1, 'wf-input', 'step-1-input')
        self.assertEqual(self.workflow, retval)
        self.assertEqual(retval.steps[0].in_[0].id, 'step-1-input')
        self.assertEqual(retval.steps[0].in_[0].source.id, 'wf-input')

    def test_connect_input_assumes_id(self):
        self.workflow.add_step(self.step1)
        retval = self.workflow.connect_input(self.step1, 'input-1')
        self.assertEqual(self.workflow, retval)
        self.assertEqual(retval.steps[0].in_[0].id, 'input-1')
        self.assertEqual(retval.steps[0].in_[0].source.id, 'input-1')

    def test_connect_steps(self):
        self.workflow.add_step(self.step1)
        self.workflow.add_step(self.step2)
        retval = self.workflow.connect_steps(self.step1, self.step2, 'step-1-output', 'step-2-input')
        self.assertEqual(self.workflow, retval)
        self.assertEqual(retval.steps[0].out[0].id, 'step-1-output')
        self.assertEqual(retval.steps[1].in_[0].source, 'my-step-1/step-1-output')
        self.assertEqual(retval.steps[1].in_[0].id, 'step-2-input')

    def test_connect_steps_assumes_id(self):
        self.workflow.add_step(self.step1)
        self.workflow.add_step(self.step2)
        retval = self.workflow.connect_steps(self.step1, self.step2, 'internal')
        self.assertEqual(self.workflow, retval)
        self.assertEqual(retval.steps[0].out[0].id, 'internal')
        self.assertEqual(retval.steps[1].in_[0].source, 'my-step-1/internal')
        self.assertEqual(retval.steps[1].in_[0].id, 'internal')

    def test_connect_output(self):
        self.workflow.add_step(self.step2)
        retval = self.workflow.connect_output(self.step2, 'step-2-output', 'wf-output')
        self.assertEqual(self.workflow, retval)
        self.assertEqual(retval.steps[0].out[0].id, 'step-2-output')
        self.assertEqual(retval.outputs[0].outputSource, 'my-step-2/step-2-output')

    def test_connect_output_assumes_id(self):
        self.workflow.add_step(self.step2)
        retval = self.workflow.connect_output(self.step2, 'output-2')
        self.assertEqual(self.workflow, retval)
        self.assertEqual(retval.steps[0].out[0].id, 'output-2')
        self.assertEqual(retval.outputs[0].outputSource, 'my-step-2/output-2')

    def test_find_step_by_id(self):
        step1_obj = WorkflowStep('step1')
        step2_obj = WorkflowStep('step2')
        self.workflow.steps = [step1_obj, step2_obj]

        self.assertEqual(self.workflow.find_step_by_id('step1'), step1_obj)
        self.assertEqual(self.workflow.find_step_by_id('step2'), step2_obj)
        with self.assertRaises(ValidationException):
            self.workflow.find_step_by_id('step3')

    def test_connect_step_to_step(self):
        step1_obj = WorkflowStep('step1')
        step2_obj = WorkflowStep('step2')
        self.workflow.steps = [step1_obj, step2_obj]
        self.workflow.connect_steps = Mock()
        self.workflow.connect_input = Mock()
        self.workflow.connect_output = Mock()

        self.workflow.connect('step1.outfield', 'step2.infield')

        self.workflow.connect_steps.assert_called_with(
            step1_obj, step2_obj, 'outfield', 'infield')
        self.workflow.connect_input.assert_not_called()
        self.workflow.connect_output.assert_not_called()

    def test_connect_input_to_step(self):
        step1_obj = WorkflowStep('step1')
        step2_obj = WorkflowStep('step2')
        self.workflow.steps = [step1_obj, step2_obj]
        self.workflow.connect_steps = Mock()
        self.workflow.connect_input = Mock()
        self.workflow.connect_output = Mock()

        self.workflow.connect('input_arg', 'step2.infield')

        self.workflow.connect_input.assert_called_with(
            step2_obj, 'input_arg', 'infield'
        )
        self.workflow.connect_steps.assert_not_called()
        self.workflow.connect_output.assert_not_called()

    def test_connect_step_to_output(self):
        step1_obj = WorkflowStep('step1')
        step2_obj = WorkflowStep('step2')
        self.workflow.steps = [step1_obj, step2_obj]
        self.workflow.connect_steps = Mock()
        self.workflow.connect_input = Mock()
        self.workflow.connect_output = Mock()

        self.workflow.connect('step2.out_field', 'output_arg')

        self.workflow.connect_output.assert_called_with(step2_obj, 'out_field', 'output_arg')
        self.workflow.connect_steps.assert_not_called()
        self.workflow.connect_input.assert_not_called()

    def test_connect_input_to_output(self):
        step1_obj = WorkflowStep('step1')
        step2_obj = WorkflowStep('step2')
        self.workflow.steps = [step1_obj, step2_obj]
        self.workflow.connect_steps = Mock()
        self.workflow.connect_input = Mock()
        self.workflow.connect_output = Mock()

        with self.assertRaises(ValidationException):
            self.workflow.connect('input_arg', 'output_arg')

        self.workflow.connect_steps.assert_not_called()
        self.workflow.connect_input.assert_not_called()
        self.workflow.connect_output.assert_not_called()
