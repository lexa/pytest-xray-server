from .constants import XRAY_EVIDENCE, XRAY_RESULT
from datetime import datetime, timedelta
from base64 import b64encode

from typing import Dict, Union
from _pytest.compat import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Literal



LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo

class XrayEvidence:
    def __init__(self, *, filename: str, data: Union[str, bytes]):
        # data should be byte-like object to be encoded in Base64
        if isinstance(data, str):
            data = data.encode()
        self.data = data
        self.filename = filename

    def as_dict(self) -> Dict[str, str]:
        return {'filename': self.filename,
                'data' : b64encode(self.data).decode()}

class XrayResult:
    def __init__(self, *, name: str, log: str, status: str):
        self.name = name
        self.log = log
        self.status = status

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
        if outcome == 'passed':
            self.status = 'PASS'
        elif outcome == 'failed':
            self.status = 'FAIL'
        elif outcome == 'skipped':
            self.status = 'TODO'
        else:
            raise Exception("XRay plugin does not understart test outcome {outcome}")
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
