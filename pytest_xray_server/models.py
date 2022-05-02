from .constants import XRAY_EVIDENCE, XRAY_RESULT
from datetime import datetime, timedelta
from base64 import b64encode
import urllib.parse

from typing import Dict, Union
from _pytest.compat import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Literal



LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo

def _convert_pytest_outcome_to_xray_status(outcome: "Literal['passed', 'failed', 'skipped']"):
    if outcome == 'passed':
        return 'PASS'
    elif outcome == 'failed':
        return 'FAIL'
    elif outcome == 'skipped':
        return 'ABORTED'
    elif outcome == 'xfailed':
        return 'XFAIL'
    else:
        raise Exception(f"Don't know how to convert status {status} to Xray status")

class XrayEvidence:
    def __init__(self, *, filename: str, data: Union[str, bytes]):
        # data should be byte-like object to be encoded in Base64
        if isinstance(data, str):
            data = data.encode()
        self.data = data
        self.filename = urllib.parse.quote(filename.replace('/', '_'))

    def as_dict(self) -> Dict[str, str]:
        return {'filename': self.filename,
                'data' : b64encode(self.data).decode()}

class XrayResult:
    def __init__(self, *, name: str, log: str, outcome: "Literal['passed', 'failed', 'skipped']" = None, status: "Literal['PASS', 'FAIL', 'TODO']" = None):
        self.name = name
        self.log = log

        assert outcome or status
        # If XRAY status is specified, use it, otherwise convert pytest outcome to status
        if status:
            self.status = status
        else:
            self.status = _convert_pytest_outcome_to_xray_status(outcome)

    def as_dict(self) -> Dict[str, str]:
        return {'name': self.name,
                'log': self.log,
                'status' : self.status}

class XrayTestReport:
    def __init__(self, test_key, test_exec_key, outcome: "Literal['passed', 'failed', 'skipped']", start, stop, evidences, results):
        self.test_key = test_key
        self.test_exec_key = test_exec_key
        self.start = datetime.fromtimestamp(start, tz=LOCAL_TIMEZONE)
        self.stop = datetime.fromtimestamp(stop, tz=LOCAL_TIMEZONE)
        self.status = _convert_pytest_outcome_to_xray_status(outcome)
        self.evidences = [e.as_dict() for e in evidences]
        self.results = [r.as_dict() for r in results]

    def __repr__(self):
        return f"<XrayTestReport ({self.status}) test_key={self.test_key}>"

    def as_dict(self):
        entry = {"testKey": self.test_key,
                 "status": self.status,
                 "start" : self.start.isoformat(timespec='seconds'),
                 "finish" : self.stop.isoformat(timespec='seconds'),
                 "evidences" : self.evidences,
                 "results" : self.results,
        }
        return entry
