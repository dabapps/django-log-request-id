import logging


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.messages = []
        super(MockLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        self.messages.append(self.format(record))
