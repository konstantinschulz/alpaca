import spacy
import language_tool_python


class Config:
    CREDIBILITY_SCORE_SERVICE = "credibility-score-service"
    DOCKER_IMAGE_CREDIBILITY_SERVICE = "konstantinschulz/credibility-score-service:v2"
    DOCKER_PORT_CREDIBILITY = 8000
    HOST_PORT_CREDIBILITY = 8181
    LANG_TOOL = language_tool_python.LanguageTool("en-US")
    NLP = spacy.load("en_core_web_sm")
    NLP_TEXT_BLOB = spacy.load("en_core_web_sm")
