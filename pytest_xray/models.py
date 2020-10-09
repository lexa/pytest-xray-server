from datetime import datetime, timedelta

from _pytest.compat import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Literal

class XrayTestReport:
    def __init__(self, outcome: Literal['passed', 'failed', 'skipped'], test_key, test_exec_key, duration, exception_log=None):
        self.test_key = test_key
        self.test_exec_key = test_exec_key
        self._set_execution_range(duration)
        if outcome == 'passed':
            self.status = 'PASS'
        elif outcome == 'failed':
            self.status = 'FAIL'
        elif outcome == 'skipped':
            self.status = 'TODO'
        else:
            raise Exception("XRay plugin does not understart test outcome {outcome}")
        self.exception_log = exception_log

    def _set_execution_range(self, duration):
        self.start_ts = datetime.utcnow()
        self.end_ts = self.start_ts + timedelta(microseconds=duration * 1000 ** 2)

    def __repr__(self):
        return f"<XrayTestReport ({self.status}) test_key={self.test_key}>"

    def as_dict(self):
        entry = {"testKey": self.test_key, "status": self.status}
        # "start": self.start_ts.isoformat()[:-7],
        # "finish": self.end_ts.isoformat()[:-7],
        if self.exception_log:
            entry["comment"] = self.exception_log
        return entry
