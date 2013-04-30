import logging
from django.test import TestCase, RequestFactory
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
