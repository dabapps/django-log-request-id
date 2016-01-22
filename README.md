django-log-request-id
=====================

**Django middleware and log filter to attach a unique ID to every log message generated as part of a request.**

**Author:** Jamie Matthews, [@j4mie](https://twitter.com/j4mie)

[![Build Status](https://travis-ci.org/dabapps/django-log-request-id.png?branch=master)](https://travis-ci.org/dabapps/django-log-request-id)

Example
-------

```
DEBUG [33031a43fc244539895fef70c433337e] myproject.apps.myapp.views: Doing something in a view
DEBUG [33031a43fc244539895fef70c433337e] myproject.apps.myapp.forms: The form validated successfully!
DEBUG [33031a43fc244539895fef70c433337e] myproject.apps.myapp.models: Doing some model magic
DEBUG [33031a43fc244539895fef70c433337e] myproject.apps.myapp.views: Redirecting to form success page
```

Why?
----

So you can grep (or otherwise search) a set of logs for a high-traffic application to isolate all messages associated with a single request.

How?
----

**The request ID is stored in a thread local**. Use of thread locals is not generally considered best practice for Django applications, but seems to be the only viable approach in this case. Pull requests with better ideas are welcome.

Any other neat features?
------------------------

In some cases, components further up the HTTP stack such as load balancers or proxies may generate request IDs. For example, [Heroku's http-request-id feature](https://devcenter.heroku.com/articles/http-request-id) adds a header to the request called `X_REQUEST_ID`. If such a header is present (and configured in your settings, see below), this ID will be used (instead of generating one). You can configure your settings to use a generated id or return a default request_id when you expect the id in the request header but it is not available.

The ID also gets added to the `HttpRequest` object that is handed to your views, in case you need to use it in your application.

If you need to pass on the ID to other services in a multi-tier architecture,
the log_request_id.session module contains a wrapper for requests.Session which
will include the ID in outgoing requests, using the same header as configured in
your settings.

Installation and usage
----------------------

First, install the package: `pip install django-log-request-id`

Add the middleware to your `MIDDLEWARE_CLASSES` setting. It should be at the very top.

```python
MIDDLEWARE_CLASSES = (
    'log_request_id.middleware.RequestIDMiddleware',
    # ... other middleware goes here
)
```

Add the `log_request_id.filters.RequestIDFilter` to your `LOGGING` setting. You'll also need to update your `formatters` to include a format with the new `request_id` variable, add a handler to output the messages (eg to the console), and finally attach the handler to your application's logger.

If none of the above made sense, study [Django's logging documentation](https://docs.djangoproject.com/en/dev/topics/logging/).

An example `LOGGING` setting is below:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        }
    },
    'formatters': {
        'standard': {
            'format': '%(levelname)-8s [%(asctime)s] [%(request_id)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['request_id'],
            'formatter': 'standard',
        },
    },
    'loggers': {
        'myapp': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
```

You can then output log messages as usual:

```python
import logging
logger = logging.getLogger(__name__)
logger.debug("A wild log message appears!")
```

If you wish to use an ID provided in a request header, add the following setting:

```python
LOG_REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
```

If you wish to fall back to a generated id when you have the `LOG_REQUEST_ID_HEADER` set but is was not provided in the request, add the following setting:

```python
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER_SETTING = True
```

If you wish to include the request id in the response headers, add the following setting:

```python
REQUEST_ID_RESPONSE_HEADER = "RESPONSE_HEADER_NAME"
```

Logging all requests
--------------------

The `RequestIDMiddleware` also has the ability to log all requests received by the application, including some useful information such as the user ID (if present). To enable this feature, add `LOG_REQUESTS = True` to your settings. The messages are sent to the `log_request_id.middleware` logger at `INFO` level.

Passing on the ID
-----------------

```python
from log_request_id.session import Session
session = Session()
session.get('http://myservice.myapp.com/')
```


License
-------

Copyright © 2012-2013, DabApps.

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
