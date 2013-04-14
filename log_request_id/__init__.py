import threading


__version__ = "0.0.1"


local = threading.local()


REQUEST_ID_HEADER_SETTING = 'LOG_REQUEST_ID_HEADER'
NO_REQUEST_ID = "none"  # Used if no request ID is available
