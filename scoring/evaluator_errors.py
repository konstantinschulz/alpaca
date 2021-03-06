import logging
import re
from config import Config
from testing import test
from parsing.webpage_data import WebpageData
from parsing.webpage_parser import has_ending_punctuation, word_tokenize

# modify grammar/spelling error score gradient given this upper limit
ERROR_LIMIT = 0.2

# boundary check
if not 0 < ERROR_LIMIT < 1:
    raise ValueError("ERROR_LIMIT must be greater than 0 and lower than 1.")

logger = logging.getLogger("alpaca")


def evaluate_errors(data: WebpageData) -> float:
    """Evaluates a webpage's language correctness.

    Determines how many spelling or grammar errors were encountered on the page and scales this value
    by overall word count. Specifically, the returned score is linear from 0 unique errors per word (no errors,
    best score => 1) to *ERRORS_LIMIT* unique errors per word (large amount of errors, worst score => 0).

    :return: Value between 0 (large amount of errors) and 1 (no errors).
    """

    # set up named entity recognition to avoid classifying names as spelling errors
    headline_ending = " " if has_ending_punctuation(data.headline) else ". " if data.headline else ""
    doc = Config.NLP(data.headline + headline_ending + data.text)
    entities = ["PERSON", "NORP", "FAC", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW"]
    names = set([ent.text for ent in doc.ents if ent.label_ in entities])
    logger.debug("[Errors] {} recognised named entities: {}".format(len(names), names))

    matches = Config.LANG_TOOL.check(data.headline)
    matches_to_ignore = 0
    if matches and matches[len(matches) - 1].ruleId == "PUNCTUATION_PARAGRAPH_END":
        # ignore error for missing punctuation at title ending
        matches.pop()
    matches += Config.LANG_TOOL.check(data.text)

    # filter out irrelevant matches and penalise errors only once
    unknown_words = []
    for match in matches:
        if (match.ruleId in ["EN_QUOTES", "DASH_RULE", "EXTREME_ADJECTIVES"] or match.category == "REDUNDANCY"
                or "is British English" in match.message or match.matchedText in unknown_words
                or ("Possible spelling mistake" in match.message
                    and any(match.matchedText in name.split() for name in names))):
            matches_to_ignore += 1
        else:
            unknown_words.append(match.matchedText)
            logger.debug("[Errors] Text error:\n{}".format(match))

    error_score = len(matches) - matches_to_ignore
    # replace variants to avoid not recognising apostrophes
    cleaned_headline = re.sub("[?????????????????????????????????]", "'", data.headline)
    word_count = len(word_tokenize(cleaned_headline)) + len(data.text_words)
    error_score = 1 - (error_score / (word_count * ERROR_LIMIT))

    logger.info("[Errors] {} grammar or spelling errors in {} words ({} errors ignored), {:.3f} errors per word"
                .format(len(matches) - matches_to_ignore, word_count, matches_to_ignore, error_score / word_count))
    test.add_result(data.url, "errors_grammar_spelling", error_score / word_count)

    return max(error_score, 0)
