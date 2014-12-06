from __future__ import division

import unittest
import tempfile
import collections

import markov_generator


class TestMarkovGenerator(unittest.TestCase):

    def load_generator(self, corpus_path, max_size):
        with tempfile.NamedTemporaryFile(
            suffix='.json', delete=True) as json_file:
            json_file.close()

            markov_generator.MarkovGenerator.write_model_file(
                corpus_path, json_file.name, max_size=max_size)
            return markov_generator.MarkovGenerator.from_model_file(
                json_file.name)

    def test_choose_sentence_finds_sentence(self):
        m = self.load_generator('testdata/corpus.txt', max_size=1)
        while True:
            sentence = m.choose_sentence()
            if (sentence ==
                'The fast brown rabbit jumps above the sleeping dog.'):
                break

    def test_choose_word_from_empty_list(self):
        m = self.load_generator('testdata/corpus.txt', max_size=3)
        self.assertIn(m.choose_word([]),
                      [(0, 'The'), (0, 'A')])

    def test_choose_word_from_length_1_list(self):
        m = self.load_generator('testdata/corpus.txt', max_size=3)
        self.assertIn(m.choose_word(['The']),
                      [(1, 'fast'), (1, 'quick')])


    def test_choose_word_from_length_2_list(self):
        m = self.load_generator('testdata/corpus.txt', max_size=3)
        self.assertIn(m.choose_word(['The', 'quick']),
                      [(2, 'brown'), (2, 'red')])

    def test_choose_word_from_length_3_list(self):
        m = self.load_generator('testdata/corpus.txt', max_size=3)
        self.assertIn(m.choose_word(['The', 'quick', 'brown']),
                      [(3, 'fox'), (3, 'rabbit')])

    def test_choose_word_from_length_4_list(self):
        m = self.load_generator('testdata/corpus.txt', max_size=3)
        self.assertIn(m.choose_word(['A', 'quick', 'brown', 'fox']),
                      [(3, 'hops'), (3, 'jumps')])

    def test_choose_word_from_length_5_list(self):
        m = self.load_generator('testdata/corpus.txt', max_size=3)
        self.assertIn(m.choose_word(['A', 'clever', 'brown', 'fox', 'jumps']),
                      [(3, 'above'), (3, 'over')])

    def test_choose_word_correct_distribution(self):
        counter = collections.Counter()
        m = self.load_generator('testdata/corpus.txt', max_size=1)
        for _ in range(10000):
            _, word = m.choose_word(['The', 'quick', 'brown'])
            counter[word] += 1

        self.assertTrue(
            8 < counter['fox']/counter['rabbit'] < 10,
            '8 < %f < 10' % (counter['fox']/counter['rabbit']))

    def test_get_num_word_options(self):
        m = self.load_generator('testdata/corpus.txt', max_size=1)
        self.assertEqual(2, m.get_num_word_options(['The', 'quick']))

    def test_get_num_word_options_only_punctuation(self):
        m = self.load_generator('testdata/corpus.txt', max_size=1)
        self.assertEqual(0, m.get_num_word_options(['lazy', 'dog']))

if __name__ == '__main__':
    unittest.main()


"""
f = MarkovGenerator.from_model_file('testdata/corpus.json')
for _ in range(100):
    print f.choose_sentence()
"""
