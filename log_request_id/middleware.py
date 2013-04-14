import uuid
from django.conf import settings
from log_request_id import local, REQUEST_ID_HEADER_SETTING, NO_REQUEST_ID


class RequestIDMiddleware(object):

    def process_request(self, request):
        request_id = self._get_request_id(request)
        local.request_id = request_id
        request.id = request_id

    def _get_request_id(self, request):
        request_id_header = getattr(settings, REQUEST_ID_HEADER_SETTING, None)
        if request_id_header:
            return request.META.get(request_id_header, NO_REQUEST_ID)
        return self._generate_id()

    def _generate_id(self):
        return uuid.uuid4().hex
