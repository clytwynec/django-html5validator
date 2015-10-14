"""
DjangoHTML5Validator Middleware Implementation
"""
import logging
import os

from django.conf import settings
from html5validator import Validator
from slugify import slugify

log = logging.getLogger('django_html5validator.middleware.validator')


class DjangoHTML5Validator(object):

    def __init__(self):
        self.report_dir = settings.DJANGO_HTML5VALIDATOR_DIR or "html_validation"
        if not os.path.isdir(self.report_dir):
            os.mkdir(self.report_dir)

        self.html_dir = os.path.join(self.report_dir, "html")
        if not os.path.isdir(self.html_dir):
            os.mkdir(self.html_dir)

        validation_log = logging.getLogger("html5validator.validator")
        validation_log_file = logging.FileHandler(
            os.path.join(self.report_dir, 'errors.txt')
        )
        validation_log.addHandler(validation_log_file)
        validation_log.propagate = False

    def process_response(self, request, response):
        if "text/html" in response["content-type"].lower() and response.content:
            html_file = os.path.join(
                self.html_dir,
                slugify(request.path) + '.html'
            )
            with open(html_file, 'w') as f:
                f.write(response.content)
                error_count = Validator().validate(files=[f.name])

            if error_count == 0:
                os.remove(html_file)

        return response
