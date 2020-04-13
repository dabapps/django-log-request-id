import logging

from django.conf import settings

from log_request_id import DEFAULT_NO_REQUEST_ID, LOG_REQUESTS_NO_SETTING, local


class RequestIDFilter(logging.Filter):

    def filter(self, record):
        default_request_id = getattr(settings, LOG_REQUESTS_NO_SETTING, DEFAULT_NO_REQUEST_ID)
        record.request_id = getattr(local, 'request_id', default_request_id)
        return True
