import unittest

from parameterized import parameterized

from tinycli.tinycli import parse_input, InputParsingError


class TestInputParser(unittest.TestCase):

    @parameterized.expand([
        [(''),          []],
        [('a'),         [(None, 'a')]],
        [('a=b'),       [('a', 'b')]],
        [(' a=b '),     [('a', 'b')]],
        [('-a b'),      [('a', 'b')]],
        [('-a=b'),      [('a', 'b')]],
        [('-a  b '),    [('a', 'b')]],
        [('--a  b'),    [('a', 'b')]],
        [('--a=b'),    [('a', 'b')]],
    ])
    def test_correct(self, input_, expected):
        result = parse_input(input_)
        self.assertEqual(result, expected)
    
    @parameterized.expand([
        ('-a -b'),
        ('--a -b'),
        ('-a 1 -b'),
        ('-a 1 --b'),
        ('--a 1 --b'),
        ('a= b='),
        ('a=1 b='),
        ('1 b='),
        ('1 -b'),
        ('--b1 a=1'),
    ])
    def test_invalid(self, input_):
        self.assertRaises(InputParsingError, parse_input, input_)
