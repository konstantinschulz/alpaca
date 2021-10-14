# Credibility Signals
## Definition
In Alpaca, credibility is determined only by the text itself, not by the author or the distributing website. Lower values correspond to lower credibility, higher values correspond to higher credibility.
## Composition
The overall credibility score is computed from a weighted combination of 24 subscores. Each of them represents a different aspect of credibility, measured directly on the text itself.
## Table of Measures and Weights
For each subscore, we give a short description of the measure and its weight factor for contribution to the overall credibility score.

|Name|Multiplier|Description|
|---|---|---|
|Authors|0.3|Verifies whether the text specifies one or more authors. Returns 1 if it does, 0 otherwise.|
|URL Domain|0.2 if the score is 1, else 0|Evaluates the text origin URL's domain ending. Returns 1 if the domain ending is .org, .edu or .gov, 0 otherwise.|
|Grammar|0.3 if the score is greater than 0.8, else 0.45|Determines how many spelling or grammar errors were encountered on the page, relative to the overall word count. Specifically, the returned score is linear from 0 unique errors per word (no errors, best score: 1) to 0.2 unique errors per word (large amount of errors, worst score: 0).|
|Questions in Text|0 if the score is greater than 0.8, else 0.2|Returned score is linear from 0 question marks per sentence (no question mark usage, best score: 1) to 0.15 question marks per sentence (high usage, worst score: 0).|
|Questions in Title|0 if there is no title, else: 0.2 if the score is greater than 0, else 0.3|1 if the title contains no question marks, else 0|
|Exclamations in Text|0 if the score is greater than 0.8, else 0.2|Returned score is linear from 0 exclamation marks per sentence (no exclamation mark usage, best score: 1) to 0.05 exclamation marks per sentence (high usage, worst score: 0).|
|Exclamations in Title|0 if there is no title, else: 0.2 if the score is greater than 0, else 0.3|1 if the title contains no exclamation marks, else 0|
|Capitalisation in Text|0 if the score is greater than 0.8, else 0.3|Capitalisation score is linear from 0 occurrences (best score: 1) to 10 occurrences (worst score: 0). Words that are all caps and occur more than once in either title or text are assumed to be acronyms or initialisms, and ignored.|
|Capitalisation in Title|0 if the title is all caps, else: 0.2 if the score is greater than 0, else 0.3|Capitalisation score is linear from 0 occurrences (best score: 1) to 2 (title) and 10 (text) occurrences (worst score: 0). Words that are all caps and occur more than once in either title or text are assumed to be acronyms or initialisms, and ignored.|
|Readability of Text|0.8|Computes and averages the Flesch-Kincaid grade level, Flesch reading ease, Gunning-Fog, SMOG, ARI and Coleman-Liau scores of the text.|
|Readability of Title|0.3|Computes and averages the Flesch-Kincaid grade level, Flesch reading ease, Gunning-Fog, SMOG, ARI and Coleman-Liau scores of the title.|
|Word Count in Text|0.5|Evaluates the number of words in the text. Returned score is linear between 300 or fewer words (worst score: 0) and 900 or more words (best score: 1).|
|Word Count in Title|0.3|Evaluates the number of words in the title. Returned score is linear between 10 or fewer words (worst score: 0) and 25 or more words (best score: 1).|
|Sentence Count|0.3|Evaluates the number of sentences in the text. Returned score is linear between 5 or fewer sentences (worst score: 0) and 30 or more sentences (best score: 1).|
|Broad Vocabulary|0.4|Type-token-ratio (TTR) is equal to the number of unique words divided by the total number of words. TTR is a measure of a text's redundancy and lexical diversity. Returned score is linear between a TTR value of 0.5 or lower (worst score: 0) and a TTR value of 1 (best score: 1).|
|Word Length in Text|0.3|Evaluates the average length of words in the text. Returned score is linear between 4 or fewer characters per word (worst score: 0) and 8 or more characters per word (best score: 1).|
|Word Length in Title|0.4|Evaluates the average length of words in the title. Returned score is linear between 4 or fewer characters per word (worst score: 0) and 8 or more characters per word (best score: 1).|
|Swearing|0 if the score is 1, else 1|Combines and checks title and text. Profanity score is linear from 0 occurrences (best score: 1) to 3 occurrences (worst score: 0).|
|Emotionality|0.6|Compares all words in the title and text against a list of emotional words with specified emotion intensity values. Sums up all intensity values for any matches, scales the total sum by word count. Final score is linear between 0 (worst score, words have on average at least 0.5 emotion intensity) and 1 (best score, words have 0 emotion intensity on average).|
|Clickbait|0 if there is not title, else: 0.3 if the score is greater than 0, else 0.8|Clickbait classifier by Alison Salerno https://github.com/AlisonSalerno/clickbait_detector|
|External Links|0.3 if the score is 1, else 0|Evaluates the usage of external (site outbound) links. Returned score is linear from 0 external links (worst score: 0) to at least 3 links (best score: 1).|
|Polarity in Text|0.8|Computes a positivity/negativity score between -1 and 1 by comparing all words in the text to a predefined list of words with polarity. Then, it looks at the absolute value as indicator of "extremism"/"emotionality". Final score is linear from 0 (absolute polarity is 1) to 1 (absolute polarity is at most 0.5).|
|Polarity in Title|0.5|Computes a positivity/negativity score between -1 and 1 by comparing all words in the title to a predefined list of words with polarity. Then, it looks at the absolute value as indicator of "extremism"/"emotionality". Final score is linear from 0 (absolute polarity is 1) to 1 (absolute polarity is at most 0.5).|
|Subjectivity|0.4|Compares each word to a predefined list of words with subjectivity. Returns a value between 0 (very high webpage subjectivity) and 1 (very low subjectivity).|
