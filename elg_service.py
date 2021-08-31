from typing import Any, Dict
from config import Config
from elg import FlaskService
from elg.model import ClassificationResponse
from scoring.credibility_evaluation_plaintext import evaluate_plaintext


class CredibilityScoreService(FlaskService):

    def convert_outputs(self, content: str) -> ClassificationResponse:
        score_dict: Dict[str, float] = evaluate_plaintext(content)
        return ClassificationResponse(classes=[{"class": k, "score": v} for k, v in score_dict.items()])

    def process_text(self, content: Any) -> ClassificationResponse:
        return self.convert_outputs(content.content)


css: CredibilityScoreService = CredibilityScoreService(Config.CREDIBILITY_SCORE_SERVICE)
app = css.app
