from datetime import datetime, timedelta

from _pytest.compat import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Literal

LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo

class XrayTestReport:
    def __init__(self, test_key, test_exec_key, outcome: Literal['passed', 'failed', 'skipped'], start, stop, exception_log=None):
        self.test_key = test_key
        self.test_exec_key = test_exec_key
        self.start = datetime.fromtimestamp(start, tz=LOCAL_TIMEZONE)
        self.stop = datetime.fromtimestamp(stop, tz=LOCAL_TIMEZONE)
        if outcome == 'passed':
            self.status = 'PASS'
        elif outcome == 'failed':
            self.status = 'FAIL'
        elif outcome == 'skipped':
            self.status = 'TODO'
        else:
            raise Exception("XRay plugin does not understart test outcome {outcome}")
        self.exception_log = exception_log

    def __repr__(self):
        return f"<XrayTestReport ({self.status}) test_key={self.test_key}>"

    def as_dict(self):
        entry = {"testKey": self.test_key,
                 "status": self.status,
                 "start" : self.start.isoformat(),
                 "finish" : self.stop.isoformat(),
        }
        if self.exception_log:
            entry["comment"] = self.exception_log
        return entry
