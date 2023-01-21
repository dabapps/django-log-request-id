import logging

try:
    from asgiref.sync import async_to_sync
except ImportError:
    async_to_sync = None

from django.contrib.sessions.backends.file import SessionStore
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase, override_settings

from log_request_id import DEFAULT_NO_REQUEST_ID, local
from log_request_id.middleware import RequestIDMiddleware
from testproject.views import test_view, test_async_view
from unittest import mock


class DummyUser(object):
    pk = 'fake_pk'
    username = 'fake_username'


class RequestIDLoggingTestCase(TestCase):
    url = "/"

    def call_view(self, request):
        return test_view(request)

    def setUp(self):
        self.factory = RequestFactory()
        self.handler = logging.getLogger('testproject').handlers[0]
        self.handler.messages = []

        # Ensure that there is nothing lurking around from previous tests
        try:
            del local.request_id
        except AttributeError:
            pass

    @mock.patch("log_request_id.middleware.RequestIDMiddleware._generate_id")
    def test_request(self, mock_generate_id):
        mock_generate_id.return_value = "test_id"
        self.client.get(self.url)
        self.assertTrue("test_id" in self.handler.messages[0])

    def test_id_generation(self):
        request = self.factory.get(self.url)
        middleware = RequestIDMiddleware(get_response=lambda request: None)
        middleware.process_request(request)
        self.assertTrue(hasattr(request, 'id'))
        self.call_view(request)
        self.assertTrue(request.id in self.handler.messages[0])

    def test_external_id_in_http_header(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER'):
            request = self.factory.get(self.url)
            request.META['REQUEST_ID_HEADER'] = 'some_request_id'
            middleware = RequestIDMiddleware(get_response=lambda request: None)
            middleware.process_request(request)
            self.assertEqual(request.id, 'some_request_id')
            self.call_view(request)
            self.assertTrue('some_request_id' in self.handler.messages[0])

    def test_default_no_request_id_is_used(self):
        request = self.factory.get(self.url)
        self.call_view(request)
        self.assertTrue(DEFAULT_NO_REQUEST_ID in self.handler.messages[0])

    @override_settings(NO_REQUEST_ID='-')
    def test_custom_request_id_is_used(self):
        request = self.factory.get(self.url)
        self.call_view(request)
        self.assertTrue('[-]' in self.handler.messages[0])

    def test_external_id_missing_in_http_header_should_fallback_to_generated_id(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER', GENERATE_REQUEST_ID_IF_NOT_IN_HEADER=True):
            request = self.factory.get(self.url)
            middleware = RequestIDMiddleware(get_response=lambda request: None)
            middleware.process_request(request)
            self.assertTrue(hasattr(request, 'id'))
            self.call_view(request)
            self.assertTrue(request.id in self.handler.messages[0])

    def test_log_requests(self):

        class DummyUser(object):
            pk = 'fake_pk'

        with self.settings(LOG_REQUESTS=True):
            request = self.factory.get(self.url)
            request.user = DummyUser()
            middleware = RequestIDMiddleware(get_response=lambda request: None)
            middleware.process_request(request)
            response = self.call_view(request)
            middleware.process_response(request, response)
            self.assertEqual(len(self.handler.messages), 2)
            self.assertTrue('fake_pk' in self.handler.messages[1])

    def test_log_user_attribute(self):
        with self.settings(LOG_REQUESTS=True, LOG_USER_ATTRIBUTE='username'):
            request = self.factory.get(self.url)
            request.user = DummyUser()
            request.session = SessionStore("session_key")
            middleware = RequestIDMiddleware(get_response=lambda request: None)
            middleware.process_request(request)
            response = self.call_view(request)
            middleware.process_response(request, response)
            self.assertEqual(len(self.handler.messages), 2)
            self.assertTrue('fake_username' in self.handler.messages[1])

    def test_log_user_attribute_anonymous_user(self):
        with self.settings(LOG_REQUESTS=True, LOG_USER_ATTRIBUTE='username'):
            request = self.factory.get(self.url)
            request.session = SessionStore()
            middleware = RequestIDMiddleware(get_response=lambda request: None)
            middleware.process_request(request)
            response = self.call_view(request)
            middleware.process_response(request, response)
            self.assertEqual(len(self.handler.messages), 2)
            self.assertFalse('fake_username' in self.handler.messages[1])
            self.assertFalse(request.session.accessed)

    def test_log_user_attribute_unset(self):
        with self.settings(LOG_REQUESTS=True, LOG_USER_ATTRIBUTE=None):
            request = self.factory.get(self.url)
            request.user = DummyUser()
            request.session = SessionStore("session_key")
            middleware = RequestIDMiddleware(get_response=lambda request: None)
            middleware.process_request(request)
            response = self.call_view(request)
            middleware.process_response(request, response)
            self.assertEqual(len(self.handler.messages), 2)
            self.assertFalse('fake_username' in self.handler.messages[1])
            self.assertFalse(request.session.accessed)

    def test_response_header_unset(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER'):
            request = self.factory.get(self.url)
            request.META['REQUEST_ID_HEADER'] = 'some_request_id'
            middleware = RequestIDMiddleware(get_response=lambda request: None)
            middleware.process_request(request)
            response = self.call_view(request)
            self.assertFalse(response.has_header('REQUEST_ID'))

    def test_response_header_set(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER', REQUEST_ID_RESPONSE_HEADER='REQUEST_ID'):
            request = self.factory.get(self.url)
            request.META['REQUEST_ID_HEADER'] = 'some_request_id'
            middleware = RequestIDMiddleware(get_response=lambda request: None)
            middleware.process_request(request)
            response = self.call_view(request)
            middleware.process_response(request, response)
            self.assertTrue(response.has_header('REQUEST_ID'))


# asgiref is required from Django 3.0
if async_to_sync:

    class AsyncRequestIDLoggingTestCase(RequestIDLoggingTestCase):
        url = "/async/"

        def call_view(self, request):
            return async_to_sync(test_async_view)(request)
