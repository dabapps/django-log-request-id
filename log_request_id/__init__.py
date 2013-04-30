import threading


__version__ = "0.0.3"


local = threading.local()


REQUEST_ID_HEADER_SETTING = 'LOG_REQUEST_ID_HEADER'
LOG_REQUESTS_SETTING = 'LOG_REQUESTS'
NO_REQUEST_ID = "none"  # Used if no request ID is available
