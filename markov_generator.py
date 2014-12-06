import json
import bisect
import random
import cStringIO
import string
import operator
import re
import collections

class NoTransitionState(Exception):
    pass


def accumulate(iterable, func=operator.add):
    'Return running totals'
    # accumulate([1,2,3,4,5]) --> 1 3 6 10 15
    # accumulate([1,2,3,4,5], operator.mul) --> 1 2 6 24 120
    it = iter(iterable)
    total = next(it)
    yield total
    for element in it:
        total = func(total, element)
        yield total


class MarkovGenerator(object):
    def __init__(self, model):
        self.model = model

    @classmethod
    def from_model_file(cls, model_path):
        with open(model_path) as f:
            return cls(json.load(f))

    @staticmethod
    def check_sentence(sentence, words):
        if words[0][0] not in string.uppercase:
            raise ValueError('Sentence does not start with uppercase: %r' % sentence)

        if words[-1] not in '?!.':
            raise ValueError('Sentence does not end correctly: %r' % sentence)

        for word in words:
            if not re.match(r"[a-zA-Z,.:;?!' ]+", word):
                raise ValueError('Sentence %r contains invalid word: %r' % (sentence, word))


    @classmethod
    def write_model_file(cls, corpus_path, model_path, max_size=5):
        from nltk import tokenize

        with open(corpus_path) as f:
            text = f.read()
            text = re.sub(r'\d+:\d+\s+', '', text)

        model = collections.defaultdict(collections.Counter)
        for sentence in tokenize.sent_tokenize(text):
            last_words = []
            words = tokenize.word_tokenize(sentence)

            try:
                cls.check_sentence(sentence, words)
            except ValueError as e:
                print e
            else:
                for word in words:
                    for size in range(1, max_size+1):
                        model[tuple(last_words[-size:])][word] += 1
                    last_words.append(word)

        bar = {}
        for last_words, next_words_counter in model.iteritems():
            choices, weights = zip(*next_words_counter.items())
            bar['_'.join(last_words)] = zip(accumulate(weights), choices)

        with open(model_path, 'wb') as f:
            json.dump(bar, f, indent=4, separators=(',', ': '))

    def _get_weighted_list(self, words):
        if not words:
            return 0, self.model['']

        for i in range(len(words)):
            weighted_choice_list = self.model.get('_'.join(words[i:]), [])
            if weighted_choice_list:
                return len(words) - i, weighted_choice_list
        raise NoTransitionState('No transitional state for: %r', words[-10:])

    def _choose_from_weighted_list(self, weighted_word_list):
        last_weight, _ = weighted_word_list[-1]
        value = random.randint(0, last_weight)
        index = bisect.bisect_left(weighted_word_list, [value, ''])
        _, word = weighted_word_list[index]
        return word

    def choose_word(self, words):
        word_matches, weighted_word_list = self._get_weighted_list(words)
        return word_matches, self._choose_from_weighted_list(weighted_word_list)

    def is_ended(self, words):
        try:
            self.choose_word(words)
        except NoTransitionState:
            return True
        else:
            return False

    def can_end(self, words):
        for i in range(len(words)):
            weighted_choice_list = self.model.get('_'.join(words[i:]), [])
            endings = set()
            for _, word in weighted_choice_list:
                if self.is_ended(words + [word]):
                    endings.add(word)

            if endings:
                return len(words) - i, random.choice(list(endings))
        return None, None

    def get_best_spelling(self, words, next_word):
        for i in range(len(words)):
            weighted_choice_list = self.model.get('_'.join(words[i:]), [])
            spellings = set()
            for _, word in weighted_choice_list:
                if word.lower() == next_word.lower():
                    spellings.add(word)
            if spellings:
                return random.choice(list(spellings))
        return next_word

    def get_num_word_options(self, words):
        word_options = set()
        for i in range(len(words)):
            weighted_choice_list = self.model.get('_'.join(words[i:]), [])
            for _, word in weighted_choice_list:
                if re.match('\w+', word):
                    word_options.add(word)
        return len(word_options)


    @staticmethod
    def words_to(words):
        last_word = None
        for word in words:
            if last_word and word[0] in string.punctuation:
                last_word += word
            else:
                if last_word is not None:
                    yield last_word
                last_word = word
        if last_word is not None:
            yield last_word

    def choose_sentence(self, words=None):
        if words is None:
            words = []

        while True:
            try:
                _, word = self.choose_word(words)
            except NoTransitionState:
                sentence = cStringIO.StringIO()
                for i, word in enumerate(words):
                    if i and not word[0] in string.punctuation:
                        sentence.write(' ')
                    sentence.write(word)
                return sentence.getvalue()
            else:
                words.append(word)

if __name__ == '__main__':
    MarkovGenerator.write_model_file('kingjames.txt', 'kingjames.json', max_size=5)
    f = MarkovGenerator.from_model_file('testdata/corpus.json')


