from unittest import TestCase

from cwlpy import InputParameter


class InputParameterTestCase(TestCase):

    def setUp(self):
        self.input_parameter = InputParameter('my-input-parameter')

    def test_id(self):
        self.assertEqual(self.input_parameter.id, 'my-input-parameter')

    def test_save(self):
        saved = self.input_parameter.save()
        self.assertEqual(saved['id'], 'my-input-parameter')
