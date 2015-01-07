from requests import Session as BaseSession
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from log_request_id import local, REQUEST_ID_HEADER_SETTING, NO_REQUEST_ID

if hasattr(settings, REQUEST_ID_HEADER_SETTING):
    REQUEST_ID_HEADER = getattr(settings, REQUEST_ID_HEADER_SETTING)
else:
    raise ImproperlyConfigured("The %s setting must be configured in order to "
                               "use %s", REQUEST_ID_HEADER_SETTING, __name__)


class Session(BaseSession):
    def prepare_request(self, request):
        """Include the request ID, if available, in the outgoing request"""
        try:
            request_id = local.request_id
        except AttributeError:
            request_id = NO_REQUEST_ID

        if REQUEST_ID_HEADER and request_id != NO_REQUEST_ID:
            request.headers[REQUEST_ID_HEADER] = request_id
