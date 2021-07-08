from typing import Any

from config import Config
from elg import FlaskService
from elg.model import ClassificationResponse
from elg.model.response.ClassificationResponse import ClassesResponse

from scoring.credibility_evaluation_plaintext import evaluate_plaintext


class CredibilityScoreService(FlaskService):

    def convert_outputs(self, content: str) -> ClassificationResponse:
        score: float = evaluate_plaintext(content)
        return ClassificationResponse(classes=[ClassesResponse(score=score)])

    def process_text(self, content: Any) -> ClassificationResponse:
        return self.convert_outputs(content.content)


css: CredibilityScoreService = CredibilityScoreService(Config.CREDIBILITY_SCORE_SERVICE)
app = css.app
