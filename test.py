from typing import Any

from config import Config
import time
import docker
from docker.models.containers import Container
from elg.model.response.ClassificationResponse import ClassificationResponse
from elg.service import Service
from elg.model import TextRequest
import unittest

from elg_service import CredibilityScoreService


class ElgTestCase(unittest.TestCase):
    content: str = "The Food and Drug Administration on Thursday extended the expiration date on hundreds of thousands of doses of Johnson & Johnson\\'s COVID-19 vaccine that otherwise would have expired within the next month, requiring them to be discarded."
    score: float = 0.7248307554041721

    def test_local(self):
        request = TextRequest(content=ElgTestCase.content)
        service = CredibilityScoreService(Config.CREDIBILITY_SCORE_SERVICE)
        response = service.process_text(request)
        self.assertEqual(response.classes[0].score, ElgTestCase.score)
        self.assertEqual(type(response), ClassificationResponse)

    def test_docker(self):
        client = docker.from_env()
        ports_dict: dict = dict()
        ports_dict[Config.DOCKER_PORT_CREDIBILITY] = Config.HOST_PORT_CREDIBILITY
        container: Container = client.containers.run(
            Config.DOCKER_IMAGE_CREDIBILITY_SERVICE, ports=ports_dict, detach=True)
        # wait for the container to start the API
        time.sleep(1)
        service: Service = Service.from_docker_image(
            Config.DOCKER_IMAGE_CREDIBILITY_SERVICE,
            f"http://localhost:{Config.DOCKER_PORT_CREDIBILITY}/process", Config.HOST_PORT_CREDIBILITY)
        response: Any = service(ElgTestCase.content, sync_mode=True)
        cr: ClassificationResponse = response
        container.stop()
        container.remove()
        self.assertEqual(cr.classes[0].score, ElgTestCase.score)
        self.assertEqual(type(response), ClassificationResponse)

    def test_elg_remote(self):
        service = Service.from_id(7348)
        response: Any = service(ElgTestCase.content)
        cr: ClassificationResponse = response
        self.assertEqual(cr.classes[0].score, ElgTestCase.score)
        self.assertEqual(type(response), ClassificationResponse)


if __name__ == '__main__':
    unittest.main()
