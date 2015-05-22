import threading


__version__ = "1.1.0"


local = threading.local()


REQUEST_ID_HEADER_SETTING = 'LOG_REQUEST_ID_HEADER'
LOG_REQUESTS_SETTING = 'LOG_REQUESTS'
NO_REQUEST_ID = "none"  # Used if no request ID is available
REQUEST_ID_RESPONSE_HEADER_SETTING = 'REQUEST_ID_RESPONSE_HEADER'
