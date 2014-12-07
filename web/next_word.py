import os
import json

import webapp2

import markov_generator

mg = markov_generator.MarkovGenerator.from_model_file('kingjames.json.bz2')


class NextWordHandler(webapp2.RequestHandler):
    def get(self):
        if self.request.get('old_words'):
            old_words = json.loads(self.request.get('old_words'))
        else:
            old_words = []

        new_word = self.request.get('new_word')
        if new_word:
            words = old_words + [mg.get_best_spelling(old_words, new_word)]
        else:
            words = old_words

        failed = False
        finished = False
        last_input_pretty_word_index = -1

        try:
            word_matches, word = mg.choose_word(words)
        except markov_generator.NoTransitionState:
            failed = True
            finished = True
            goodness = 0
            if words:
                last_input_pretty_word_index = len(list(mg.words_to(words))) - 1
        else:
            if words:
                goodness = min(1, word_matches / min(3, len(words)))
                last_input_pretty_word_index = len(list(mg.words_to(words))) - 1
            else:
                goodness = 1.0
            words.append(word)

            while mg.get_num_word_options(words) < 15:
                try:
                    _, word = mg.choose_word(words)
                    words.append(word)
                except markov_generator.NoTransitionState:
                    finished = True
                    break

            ending_word_matches, ending_word = mg.can_end(words)
            if  (ending_word and
                 ((len(words) > 10 and ending_word_matches > 3) or
                  (len(words) > 15 and ending_word_matches > 2) or
                  (len(words) > 20 and ending_word_matches > 1) or
                  (len(words) > 25))):
                words.append(ending_word)
                finished = True


        response = {
            'pretty_words': list(mg.words_to(words)),
            'last_input_pretty_word_index': last_input_pretty_word_index,
            'words': words,
            'finished': finished,
            'failed': failed,
            'goodness': goodness
        }
        self.response.write(json.dumps(response))

app = webapp2.WSGIApplication([('/nextword', NextWordHandler)], debug=True)
