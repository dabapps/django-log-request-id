import logging
from log_request_id import local, NO_REQUEST_ID


class RequestIDFilter(logging.Filter):

    def __init__(self, name='', request_id_attr='request_id'):
        self.request_id_attr = request_id_attr
        super(RequestIDFilter, self).__init__(name)

    def filter(self, record):
        setattr(record, self.request_id_attr,
                getattr(local, 'request_id', NO_REQUEST_ID))
        return True
