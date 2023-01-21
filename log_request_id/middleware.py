import logging
import uuid

from django.conf import settings
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object
from log_request_id import local, REQUEST_ID_HEADER_SETTING, LOG_REQUESTS_SETTING, DEFAULT_NO_REQUEST_ID, \
    REQUEST_ID_RESPONSE_HEADER_SETTING, GENERATE_REQUEST_ID_IF_NOT_IN_HEADER_SETTING, LOG_REQUESTS_NO_SETTING, \
    LOG_USER_ATTRIBUTE_SETTING


logger = logging.getLogger(__name__)


class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request_id = self._get_request_id(request)
        local.request_id = request_id
        request.id = request_id

    def get_log_message(self, request, response):
        message = 'method=%s path=%s status=%s' % (request.method, request.path, response.status_code)

        # `LOG_USER_ATTRIBUTE_SETTING` accepts False/None to skip setting attribute
        #  but falls back to 'pk' if value is not set
        user_attribute = getattr(settings, LOG_USER_ATTRIBUTE_SETTING, 'pk')
        if not user_attribute:
            return message

        # avoid accessing session if it is empty
        if getattr(request, 'session', None) and request.session.is_empty():
            return message

        user = getattr(request, 'user', None)
        if not user:
            return message

        user_id = getattr(user, user_attribute, None) or getattr(user, 'id', None)
        message += ' user=' + str(user_id)
        return message

    def process_response(self, request, response):
        if getattr(settings, REQUEST_ID_RESPONSE_HEADER_SETTING, False) and getattr(request, 'id', None):
            response[getattr(settings, REQUEST_ID_RESPONSE_HEADER_SETTING)] = request.id

        if not getattr(settings, LOG_REQUESTS_SETTING, False):
            return response

        # Don't log favicon
        if 'favicon' in request.path:
            return response

        logger.info(self.get_log_message(request, response))

        try:
            del local.request_id
        except AttributeError:
            pass

        return response

    def _get_request_id(self, request):
        request_id_header = getattr(settings, REQUEST_ID_HEADER_SETTING, None)
        generate_request_if_not_in_header = getattr(settings, GENERATE_REQUEST_ID_IF_NOT_IN_HEADER_SETTING, False)

        if request_id_header:
            # fallback to NO_REQUEST_ID if settings asked to use the
            # header request_id but none provided
            default_request_id = getattr(settings, LOG_REQUESTS_NO_SETTING, DEFAULT_NO_REQUEST_ID)

            # unless the setting GENERATE_REQUEST_ID_IF_NOT_IN_HEADER
            # was set, in which case generate an id as normal if it wasn't
            # passed in via the header
            if generate_request_if_not_in_header:
                default_request_id = self._generate_id()

            return request.META.get(request_id_header, default_request_id)

        return self._generate_id()

    def _generate_id(self):
        return uuid.uuid4().hex
