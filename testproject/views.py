import logging
from django.http import HttpResponse


logger = logging.getLogger(__name__)


def test_view(request):
    logger.debug("A wild log message appears!")
    return HttpResponse('ok')
