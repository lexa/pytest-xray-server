from os import environ

import pytest

from .constants import XRAY_API_BASE_URL_DEFAULT, XRAY_PLUGIN, XRAY_MARKER_NAME
from .models import XrayTestReport
from .utils import PublishXrayResults

JIRA_XRAY_FLAG = "--jira-xray"


def pytest_configure(config):
    if not config.getoption(JIRA_XRAY_FLAG):
        return

    config.addinivalue_line("markers",
                            f"{XRAY_MARKER_NAME}(test_key, test_exec_key): report test results to Jira/Xray")

    plugin = XRayReporter()
    config.pluginmanager.register(plugin, XRAY_PLUGIN)


def pytest_addoption(parser):
    group = parser.getgroup("JIRA Xray integration")

    group.addoption(
        JIRA_XRAY_FLAG, action="store_true", help="jira_xray: Publish test results to Xray API"
    )

    parser.addini('xray_base_url', help="URL of Jira/XRAY API entry point ", default=XRAY_API_BASE_URL_DEFAULT)

# Test is considered PASSED iff 'setup', 'call' and 'teardown' phases are successful
# If any of phases fail, the test reported as 'failed'
# If any of pases are skipped, the test is reported as 'TODO'
class XRayReporter:

    def __init__(self):
        self._results = []#type: List[XrayTestReport]
        self._outcomes = dict()# type: Dict[str, Literal['failed', 'skipped', 'passed']]

    def _update_outcome(self, nodeid: str, outcome: Literal['failed', 'skipped', 'passed']):
        prev_outcome = self._outcomes.get(nodeid, outcome)

        if "failed" in [prev_outcome, outcome]:
             self._outcomes[nodeid] = 'failed'
        elif "skipped" in [prev_outcome, outcome]:
             self._outcomes[nodeid] = 'skipped'
        elif prev_outcome == 'passed' and outcome == 'passed':
             self._outcomes[nodeid] = 'passed'
        else:
             raise Exception(f"{nodeid} : Can't handle outcome {outcome} and previous outcome {prev_outcome}")

        return self._outcomes[nodeid]

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: "pytest.Item", call: "_pytest.runner.CallInfo[None]") -> Generator:
        marker = item.get_closest_marker(XRAY_MARKER_NAME)
        if not marker:
            return

        outcome = yield
        rep = outcome.get_result()

        outcome = self._update_outcome(item.nodeid, rep.outcome)

        if rep.when == 'teardown':
            self._results.append(XrayTestReport(marker.kwargs["test_key"],
                                                marker.kwargs["test_exec_key"],
                                                outcome,
                                                call.start,
                                                call.stop
            ))

    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        reporter = PublishXrayResults(
            session.config.getini('xray_base_url'),
            client_id=environ["XRAY_API_CLIENT_ID"],
            client_secret=environ["XRAY_API_CLIENT_SECRET"],
        )
        reporter(self._results)
