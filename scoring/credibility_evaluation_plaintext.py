import re

import nltk
from parsing.webpage_data import WebpageData
import parsing.webpage_parser as parser
import logging
from .credibility_evaluation import evaluation_signals
from testing import test


logger = logging.getLogger("alpaca")


def evaluate_plaintext(text: str) -> float:
    """Scores a text's credibility by combining the credibility scores of different evaluators.

    Retrieves the signal sub-scores, validates the results and then generates an
    overall text credibility score via linear combination of the sub-scores using the *evaluation_weights* dict.

    :param text: Text to be evaluated.
    :return: A credibility score from 0 (very low credibility) to 1 (very high credibility).
        Returns -2 if the text could not be evaluated.
    """

    # tokenize text, replacing symbols that are problematic for tokenizers
    tokenizer_text = re.sub("[“‟„”«»❝❞⹂〝〞〟＂]", "\"",
                            re.sub("[‹›’❮❯‚‘‛❛❜❟]", "'", text))
    sentences = nltk.sent_tokenize(tokenizer_text)
    words = parser.word_tokenize(tokenizer_text)
    page_data = WebpageData(text=text, text_words=words,
                            text_sentences=sentences, headline=sentences[0])

    scores = {}
    weight_sum = 0
    final_score = 0

    # compute sub-scores and sum up overall score via linear combination
    # TODO possibly parellelise the signal evaluation calls to boost performance
    for signal_name, signal in evaluation_signals.items():
        subscore = signal.evaluator(page_data)
        weight = signal.weight_func(subscore, page_data)
        scores[signal_name] = subscore
        final_score += subscore * weight
        weight_sum += weight
        test.add_result(text, "score_" + signal_name, subscore)

    # check for valid scores
    if not scores or len(scores) != len(evaluation_signals) or not all(0 <= score <= 1 for score in scores.values()):
        logger.error(
            "[Evaluation] Error computing sub-scores: {}".format(scores))
        return -2

    logger.info("[Evaluation] Individual sub-scores: {}".format(
        [signal_name + " {:.3f}".format(score) for signal_name, score in scores.items()]))

    final_score = final_score / weight_sum
    logger.debug(
        "[Evaluation] Overall webpage score: {:.5f} for '{}'".format(final_score, text[:20]))
    return final_score
