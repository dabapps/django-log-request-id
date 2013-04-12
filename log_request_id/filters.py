import logging
import threading
from log_request_id import NO_REQUEST_ID


local = threading.local()


class RequestIDFilter(logging.Filter):

    def filter(self, record):
        record.request_id = getattr(local, 'request_id', NO_REQUEST_ID)
        return True
