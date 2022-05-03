from os import environ

import time
import pytest

from .constants import XRAY_API_BASE_URL_DEFAULT, XRAY_PLUGIN, XRAY_MARKER_NAME, XRAY_EVIDENCE, XRAY_RESULT, JIRA_XRAY_FLAG, XRAY_TEST_EXEC_ARG
from .models import XrayTestReport, XrayEvidence, XrayResult
from .utils import PublishXrayResults, xray_evidence, xray_result

from typing import List, Dict, Generator
from _pytest.compat import TYPE_CHECKING
from _pytest.runner import Item, TestReport
if TYPE_CHECKING:
    from typing_extensions import Literal


def pytest_configure(config):
    config.addinivalue_line("markers",
                            f"{XRAY_MARKER_NAME}(test_key, test_exec_key): report test results to Jira/Xray")

    if not config.getoption(JIRA_XRAY_FLAG):
        return

    plugin = XRayReporter(config)
    config.pluginmanager.register(plugin, XRAY_PLUGIN)


def pytest_addoption(parser):
    group = parser.getgroup("JIRA Xray integration")

    group.addoption(
        JIRA_XRAY_FLAG, action="store_true", help="jira_xray: Publish test results to Xray API"
    )

    group.addoption(
        XRAY_TEST_EXEC_ARG, action="store", help="jira_xray: Test execution Ticket ID"
    )

    parser.addini('xray_base_url', help="URL of Jira/XRAY API entry point ", default=XRAY_API_BASE_URL_DEFAULT)

# Test is considered PASSED iff 'setup', 'call' and 'teardown' phases are successful
# If any of phases fail, the test reported as 'failed'
# If any of pases are skipped, the test is reported as 'TODO'
class XRayReporter:

    def __init__(self, config):
        self._default_test_exec_key = config.getoption(XRAY_TEST_EXEC_ARG)
        self._results = []#type: List[XrayTestReport]
        self._outcomes = dict()# type: Dict[str, Literal['failed', 'skipped', 'passed']]
        self._ticket_id = dict()# type: Dict[str, Tiple[str, str]]
        self.reporter = PublishXrayResults(
            config.getini('xray_base_url'),
            client_id=environ["XRAY_API_CLIENT_ID"],
            client_secret=environ["XRAY_API_CLIENT_SECRET"],
        )

    def _update_outcome(self, nodeid: str, outcome: "Literal['failed', 'skipped', 'passed']"):
        prev_outcome = self._outcomes.get(nodeid, outcome)

        if "failed" in [prev_outcome, outcome]:
             self._outcomes[nodeid] = 'failed'
        elif "skipped" in [prev_outcome, outcome]:
             self._outcomes[nodeid] = 'skipped'
        elif "xfailed" in [prev_outcome, outcome]:
             self._outcomes[nodeid] = 'xfailed'
        elif prev_outcome == 'passed' and outcome == 'passed':
             self._outcomes[nodeid] = 'passed'
        else:
             raise Exception(f"{nodeid} : Can't handle outcome {outcome} and previous outcome {prev_outcome}")

        return self._outcomes[nodeid]

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_setup(self, item: "Item") -> None:
        marker = item.get_closest_marker(XRAY_MARKER_NAME)
        if not marker:
            return

        test_exec_key = marker.kwargs.get("test_exec_key", None) or self._default_test_exec_key
        if not test_exec_key:
            raise pytest.UsageError("test {} does not have test_exec_key configured and no command line option {} specified".format(item.nodeid, XRAY_TEST_EXEC_ARG))
        self._ticket_id[item.nodeid] = (test_exec_key , marker.kwargs["test_key"])

    
    def pytest_runtest_logreport(self, report: "TestReport"):
        test_exec_key, test_key = self._ticket_id.get(report.nodeid, (None, None))
        if not (test_exec_key and test_key):
            return

        if getattr(report, 'keywords', ()).get('xfail', 0): 
            report.outcome = 'xfailed'
        outcome = self._update_outcome(report.nodeid, report.outcome)

        if report.when != 'teardown':
            return

        evidences = [e for n, e in report.user_properties if n == XRAY_EVIDENCE]
        results = [r for n, r in report.user_properties if n == XRAY_RESULT]

        self._results.append(XrayTestReport(test_key,
                                            test_exec_key,
                                            outcome,
                                            time.time() - report.duration,
                                            time.time(),
                                            evidences,
                                            results
                                            ))

    def pytest_sessionfinish(self, session: pytest.Session) -> None:

        self.reporter(self._results)
