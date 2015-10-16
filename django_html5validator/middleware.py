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
    """
    A Django middleware class for checking "text/html" responses for html
    validation issues.
    """
    def __init__(self):
        if hasattr(settings, "DJANGO_HTML5VALIDATOR_DIR"):
            self.report_dir = settings.DJANGO_HTML5VALIDATOR_DIR
        else:
            self.report_dir = "html_validation"

        if not os.path.isdir(self.report_dir):
            os.makedirs(self.report_dir)

        self.html_dir = os.path.join(self.report_dir, "html")
        if not os.path.isdir(self.html_dir):
            os.makedirs(self.html_dir)

        validation_log = logging.getLogger("html5validator.validator")
        validation_log_file = logging.FileHandler(
            os.path.join(self.report_dir, 'errors.txt')
        )
        validation_log.addHandler(validation_log_file)
        validation_log.propagate = False

    def process_response(self, request, response):
        """
        Checks any "text/html" response for HTML validation issues.

        An `errors.txt` file will be created in an `html_validation` directory
        or DJANGO_HTML5VALIDATOR_DIR. This file will containing the HTML error
        messages. An `html` folder will be created in the same directory and
        will contain the html content that has validation issues.
        """
        try:
            content_type = response["content-type"].lower()
        except TypeError:
            content_type = response.headers["content-type"].lower()

        if "text/html" in content_type and response.content:

            html_file_path = os.path.join(
                self.html_dir,
                slugify(request.path, max_length=250) + '.html'
            )
            with open(html_file_path, 'w') as html_file:
                html_file.write(response.content)
                file_name = html_file.name

            error_count = Validator().validate(files=[file_name])

            if error_count == 0:
                os.remove(html_file_path)

        return response
