import unittest
from bot import Memory, parse_verdict

class Tests(unittest.TestCase):
    def test_context_and_best(self):
        m = Memory(':memory:')
        m.record(['rock'], 'paper', True, 'covers')
        m.record(['rock','paper'], 'fire', True, 'burns')
        m.record(['rock','paper','fire'], 'water', False, 'rejected here')
        self.assertFalse(m.allowed(['rock','paper','fire'], 'water'))
        self.assertTrue(m.allowed(['rock','fire'], 'water'))
        self.assertFalse(m.allowed(['rock','paper'], ' ROCK '))
        self.assertEqual(m.best(), ['rock','paper','fire'])
        self.assertGreater(m.value(['rock'], 'paper'), m.value(['rock'], 'scissors'))

    def test_verdict_not_loading_or_ad(self):
        self.assertIsNone(parse_verdict(['what beats','rock?','paper','paper','paper'], 'rock','paper'))
        self.assertIsNone(parse_verdict(['paper','beats','scissors'], 'rock','paper'))
        self.assertEqual(parse_verdict(['paper','beats','rock','covers'], 'rock','paper'), (True,'covers'))
        self.assertEqual(parse_verdict(['feather','does not beat','rock','too weak'], 'rock','feather'), (False,'too weak'))

if __name__ == '__main__':
    unittest.main()
