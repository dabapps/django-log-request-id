import logging
from django.test import TestCase, RequestFactory
from django.core.exceptions import ImproperlyConfigured
from requests import Request

from log_request_id.middleware import RequestIDMiddleware
from testproject.views import test_view


class RequestIDLoggingTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.handler = logging.getLogger('testproject').handlers[0]
        self.handler.messages = []

    def test_id_generation(self):
        request = self.factory.get('/')
        middleware = RequestIDMiddleware()
        middleware.process_request(request)
        self.assertTrue(hasattr(request, 'id'))
        test_view(request)
        self.assertTrue(request.id in self.handler.messages[0])

    def test_external_id_in_http_header(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER'):
            request = self.factory.get('/')
            request.META['REQUEST_ID_HEADER'] = 'some_request_id'
            middleware = RequestIDMiddleware()
            middleware.process_request(request)
            self.assertEqual(request.id, 'some_request_id')
            test_view(request)
            self.assertTrue('some_request_id' in self.handler.messages[0])

    def test_external_id_missing_in_http_header_should_fallback_to_generated_id(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER', GENERATE_REQUEST_ID_IF_NOT_IN_HEADER=True):
            request = self.factory.get('/')
            middleware = RequestIDMiddleware()
            middleware.process_request(request)
            self.assertTrue(hasattr(request, 'id'))
            test_view(request)
            self.assertTrue(request.id in self.handler.messages[0])

    def test_log_requests(self):

        class DummyUser(object):
            pk = 'fake_pk'

        with self.settings(LOG_REQUESTS=True):
            request = self.factory.get('/')
            request.user = DummyUser()
            middleware = RequestIDMiddleware()
            middleware.process_request(request)
            response = test_view(request)
            middleware.process_response(request, response)
            self.assertEqual(len(self.handler.messages), 2)
            self.assertTrue('fake_pk' in self.handler.messages[1])

    def test_response_header_unset(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER'):
            request = self.factory.get('/')
            request.META['REQUEST_ID_HEADER'] = 'some_request_id'
            middleware = RequestIDMiddleware()
            middleware.process_request(request)
            response = test_view(request)
            self.assertFalse(response.has_header('REQUEST_ID'))

    def test_response_header_set(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER', REQUEST_ID_RESPONSE_HEADER='REQUEST_ID'):
            request = self.factory.get('/')
            request.META['REQUEST_ID_HEADER'] = 'some_request_id'
            middleware = RequestIDMiddleware()
            middleware.process_request(request)
            response = test_view(request)
            middleware.process_response(request, response)
            self.assertTrue(response.has_header('REQUEST_ID'))


class RequestIDPassthroughTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_request_id_passthrough_with_custom_header(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER', OUTGOING_REQUEST_ID_HEADER='OUTGOING_REQUEST_ID_HEADER'):
            from log_request_id.session import Session
            request = self.factory.get('/')
            request.META['REQUEST_ID_HEADER'] = 'some_request_id'
            middleware = RequestIDMiddleware()
            middleware.process_request(request)
            self.assertEqual(request.id, 'some_request_id')
            session = Session()
            outgoing = Request('get', 'http://nowhere')
            session.prepare_request(outgoing)
            self.assertEqual(
                outgoing.headers['OUTGOING_REQUEST_ID_HEADER'],
                'some_request_id'
            )

    def test_request_id_passthrough(self):
        with self.settings(LOG_REQUEST_ID_HEADER='REQUEST_ID_HEADER'):
            from log_request_id.session import Session
            request = self.factory.get('/')
            request.META['REQUEST_ID_HEADER'] = 'some_request_id'
            middleware = RequestIDMiddleware()
            middleware.process_request(request)
            self.assertEqual(request.id, 'some_request_id')
            session = Session()
            outgoing = Request('get', 'http://nowhere')
            session.prepare_request(outgoing)
            self.assertEqual(
                outgoing.headers['REQUEST_ID_HEADER'],
                'some_request_id'
            )

    def test_misconfigured_for_sessions(self):
        def inner():
            from log_request_id.session import Session  # noqa
            Session()
        self.assertRaises(ImproperlyConfigured, inner)
