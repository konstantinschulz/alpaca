import logging
import re

import _readability as readability
import test
from parsing.webpage_data import WebpageData

# modify readability text length score (words/sentences/paragraphs sub-score gradients) given these upper limits
WORDS_LIMIT_LOWER = 300
WORDS_LIMIT_UPPER = 900
SENTENCE_LIMIT_LOWER = 10
SENTENCE_LIMIT_UPPER = 20
PARAGRAPH_LIMIT_LOWER = 1
PARAGRAPH_LIMIT_UPPER = 2.5

# boundary checks
if (WORDS_LIMIT_LOWER < 1 or SENTENCE_LIMIT_LOWER < 1 or PARAGRAPH_LIMIT_LOWER < 1
        or WORDS_LIMIT_UPPER <= WORDS_LIMIT_LOWER or SENTENCE_LIMIT_UPPER <= SENTENCE_LIMIT_LOWER
        or PARAGRAPH_LIMIT_UPPER <= PARAGRAPH_LIMIT_LOWER):
    raise ValueError("A constant for text length evaluation is set incorrectly")

logger = logging.getLogger("alpaca")


def evaluate_readability_grades(data: WebpageData) -> float:
    """Evaluates the readability of a webpage by averaging several common readability grades.

    Computes and combines (with equal weight) the Flesch-Kincaid grade level, Flesch reading ease,
    Gunning-Fog, SMOG, ARI and Coleman-Liau scores of the webpage headline and main text.

    :return: Combined readability score between 0 and 1, with 0 indicating easy understandability (low text complexity)
        and 1 indicating hard understandability (high text complexity).
    """

    # TODO analyse which readability grades perform best as indicators of credibility and exclude the others (?)

    read_metrics = readability.getmeasures(data.tokenized_text, lang="en")
    paragraph_count = data.text.count("\n") + 1

    logger.debug("[Readability] Text properties: "
                 "{} characters | {} syllables | {} words | {} sentences | {} paragraphs | "
                 "{:.3f} characters_p_w | {:.3f} syllables_p_w | {:.3f} words_p_s | {:.3f} sentences_p_p | "
                 "{} word types | {} long words | {} complex words"
                 .format(read_metrics["sentence info"]["characters"],  # alphanumeric symbols and hyphens (-)
                         read_metrics["sentence info"]["syllables"],
                         read_metrics["sentence info"]["words"],  # strings of alphanumerics & hyphens (isn't = 2 words)
                         read_metrics["sentence info"]["sentences"],
                         paragraph_count,
                         read_metrics["sentence info"]["characters_per_word"],
                         read_metrics["sentence info"]["syll_per_word"],
                         read_metrics["sentence info"]["words_per_sentence"],
                         read_metrics["sentence info"]["sentences"] / paragraph_count,
                         read_metrics["sentence info"]["wordtypes"],
                         read_metrics["sentence info"]["long_words"],
                         read_metrics["sentence info"]["complex_words"]))
    logger.debug("[Readability] Readability grades: "
                 "Flesch-Kincaid grade {:.3f} | Flesch reading ease {:.3f} | "
                 "Gunning-Fog {:.3f} | SMOG {:.3f} | ARI {:.3f} | Coleman-Liau {:.3f}"
                 .format(read_metrics["readability grades"]["Kincaid"],
                         read_metrics["readability grades"]["FleschReadingEase"],
                         read_metrics["readability grades"]["GunningFogIndex"],
                         read_metrics["readability grades"]["SMOGIndex"],
                         read_metrics["readability grades"]["ARI"],
                         read_metrics["readability grades"]["Coleman-Liau"]))
    test.add_result(data.url, "flesch_kincaid", read_metrics["readability grades"]["Kincaid"])
    test.add_result(data.url, "flesch_reading_ease", read_metrics["readability grades"]["FleschReadingEase"])
    test.add_result(data.url, "gunning_fog", read_metrics["readability grades"]["GunningFogIndex"])
    test.add_result(data.url, "smog", read_metrics["readability grades"]["SMOGIndex"])
    test.add_result(data.url, "ari", read_metrics["readability grades"]["ARI"])
    test.add_result(data.url, "coleman_liau", read_metrics["readability grades"]["Coleman-Liau"])

    # preliminary scoring: assign highest credibility for complex text, equivalent to  11th-grade reading level
    # Flesch-Kincaid grade level score range 1-17, 11-17 best
    # Flesch reading ease score range 1-100, 1-50 best
    # Gunning-Fog score range 1-17, 11-17 best
    # SMOG score range 5-22, 16-22 best
    # ARI score range 1-14, 11-14 best
    # Coleman-Liau score range 1-17, 11-17 best
    readability_scores = [(11 - read_metrics["readability grades"]["Kincaid"]) / 10,
                          1 - ((100 - read_metrics["readability grades"]["FleschReadingEase"]) / 50),
                          (11 - read_metrics["readability grades"]["GunningFogIndex"]) / 10,
                          (16 - read_metrics["readability grades"]["SMOGIndex"]) / 11,
                          (11 - read_metrics["readability grades"]["ARI"]) / 10,
                          (11 - read_metrics["readability grades"]["Coleman-Liau"]) / 10]

    for index, score in enumerate(readability_scores):
        readability_scores[index] = 1 - max(min(score, 1), 0)
    logger.info("[Readability] Readability scores: {}".format([round(score, 3) for score in readability_scores]))

    # lower median
    readability_scores.sort()
    return readability_scores[2]


# TODO incorporate #chars1, #words2, #sentences3, #paragraphs2, paragraph length1, sentence length2, word length1

def evaluate_text_lengths(data: WebpageData) -> float:
    """Evaluates the absolute number of words & average sentence and paragraph length of a webpage's text.

    Computes subscores for overall word count, average sentence length  and paragraph length. The subscores are linear
    from at or below *LIMIT_LOWER* (very short text/sentences/paragraphs, worst score => 1) to at or above *LIMIT_UPPER*
    (long text/sentences/paragraphs, best score => 1). The three scores are averaged into the returned overall score,
    with text length (word count) being double-weighted. Returns 0 if no sentence-ending punctuation is detected.

    :return: Combined score for number of words & average sentence and paragraph length between 0 and 1, with 0
    indicating very short texts with short sentences and paragraphs and 1 indicating long texts/sentences/paragraphs.
    """

    # word score
    # words are strings bounded by whitespaces + 1, excluding strings consisting of a single non-alphanumeric character
    word_count = data.text.count(" ") + 1 - len(re.findall(r"\s\W\s", data.text))
    word_score = (word_count - WORDS_LIMIT_LOWER) / (WORDS_LIMIT_UPPER - WORDS_LIMIT_LOWER)
    word_score = min(max(word_score, 0), 1)

    # sentence score
    sentence_count = len(data.tokenized_text)
    if sentence_count == 0:
        logger.warning("[Readability] No sentences detected.")
        return 0
    sentence_length = word_count / sentence_count
    sentence_score = (sentence_length - SENTENCE_LIMIT_LOWER) / (SENTENCE_LIMIT_UPPER - SENTENCE_LIMIT_LOWER)
    sentence_score = min(max(sentence_score, 0), 1)

    # paragraph score
    paragraph_length = sentence_count / (data.text.count("\n") + 1)
    paragraph_score = (paragraph_length - PARAGRAPH_LIMIT_LOWER) / (PARAGRAPH_LIMIT_UPPER - PARAGRAPH_LIMIT_LOWER)
    paragraph_score = min(max(paragraph_score, 0), 1)

    logger.info("[Readability] {} words (subscore {:.3f}) | {:.3f} average sentence length (subscore {:.3f}) | "
                "{:.3f} average paragraph length (subscore {:.3f})"
                .format(word_count, word_score, sentence_length, sentence_score, paragraph_length, paragraph_score))

    return (2 * word_score + sentence_score + paragraph_score) / 4
