import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from bot import Memory, parse_verdict, parse_candidates, choose, export

class Tests(unittest.TestCase):
    def test_context_and_best(self):
        m = Memory(':memory:')
        self.addCleanup(m.db.close)
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
        self.assertEqual(parse_verdict(['nothing','does not beat','feather',
                        '28 other people already tried this','A feather is still something.'],
                        'feather','nothing'), (False,'A feather is still something.'))

    def test_persistence_and_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            m = Memory(path/'memory.sqlite3')
            m.record(['rock'], 'paper', True, 'covers')
            m.record(['rock','paper'], 'nothing', False, 'weak')
            m.db.close()
            m = Memory(path/'memory.sqlite3')
            self.assertEqual(m.best(), ['rock','paper'])
            self.assertFalse(m.allowed(['rock','paper'], 'nothing'))
            export(m, path)
            self.assertIn('paper', (path/'best_chain.json').read_text())
            m.db.close()

    def test_exploration_filters_rejected_and_repeated(self):
        m = Memory(':memory:')
        self.addCleanup(m.db.close)
        m.record(['rock'], 'nothing', False, 'no')
        with patch('bot.proposals', return_value=['rock', 'nothing', 'paper']):
            self.assertEqual(choose(m, ['rock'], object(), 1), 'paper')
        # Once known, the successful link remains usable without invoking the model.
        m.record(['rock'], 'paper', True, 'yes')
        with patch('bot.proposals', side_effect=AssertionError('Unexpected model call')):
            self.assertEqual(choose(m, ['rock'], object(), 0), 'paper')

    def test_malformed_model_output(self):
        self.assertEqual(parse_candidates('{"candidates":[" Paper ","paper",3,""]}'), ['paper'])
        with self.assertRaises(ValueError):
            parse_candidates('{"candidates": "paper"}')

if __name__ == '__main__':
    unittest.main()
