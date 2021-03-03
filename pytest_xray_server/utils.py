import json
import logging

import pytest
import requests
from typing import Union

from requests.auth import HTTPBasicAuth

from .constants import XRAY_MARKER_NAME, XRAY_EVIDENCE, XRAY_RESULT
from .models import XrayEvidence, XrayResult

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PublishXrayResults:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret

    def __call__(self, *report_objs):
        for a_dict in self._test_execution_summaries(*report_objs):
            self._post(a_dict)

        logger.info("Successfully posted all test execution results to Xray!")

    def _post(self, a_dict):
        logger.debug(f"Payload => {a_dict}")
        url = self.results_url()
        resp = requests.post(self.results_url(), json=a_dict, auth=HTTPBasicAuth(self.client_id, self.client_secret))
        resp.raise_for_status()

    def results_url(self):
        return f"{self.base_url}/raven/1.0/import/execution"

    def _test_execution_summaries(self, report_objs):
        summaries = {}

        for each in report_objs:
            if not each.test_exec_key in summaries:
                summaries[each.test_exec_key] = self._create_header(each.test_exec_key)
            summaries[each.test_exec_key]["tests"].append(each.as_dict())

        return summaries.values()

    def _create_header(self, test_exec_key):
        return {
            "testExecutionKey": test_exec_key,
            "info": {
                "summary": "Execution of automated tests",
                "description": "",
                "testEnvironments": [],
            },
            "tests": [],
        }

@pytest.fixture()
def xray_evidence(request):
    """Capture a binary file to attach to Xray execution ticket"""
    def _xray_evidence(filename: str, data: Union[str, bytes]):
        request.node.user_properties.append((XRAY_EVIDENCE, XrayEvidence(filename=filename, data=data)))

    return _xray_evidence

@pytest.fixture()
def xray_result(request):
    """Capture a chunk of text to attach to Xray execution ticket"""
    def _xray_result(name: str, log : str, outcome: "Literal['passed', 'failed', 'skipped']"):
        request.node.user_properties.append((XRAY_RESULT, XrayResult(name, log, outcome)))

    return _xray_result
