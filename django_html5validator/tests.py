"""
Tests for the middleware
"""
import httpretty
import os
import requests

from django.conf import settings
from django.test.utils import override_settings
from django_html5validator.middleware import DjangoHTML5Validator
from mock import Mock
from shutil import rmtree
from textwrap import dedent
from unittest import TestCase

# Configure basic settings
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test.db',
            'TEST_NAME': 'test.db',
        }
    },
)


class DjangoHTML5ValidatorTestCase(TestCase):
    """
    Unit tests for the DjangoHTML5Validator middleware.
    """
    def setUp(self):
        self.output_dir = "html_validation"
        self.html_dir = os.path.join(self.output_dir, "html")
        self.errors_file = os.path.join(self.output_dir, "errors.txt")

        self.addCleanup(rmtree, self.output_dir)
        self.request = Mock()

    def test_init_default(self):
        """
        Test initializing with default settings.
        """
        validator = DjangoHTML5Validator()
        self.assertEqual(validator.report_dir, self.output_dir)
        self.assertEqual(validator.html_dir, self.html_dir)

    @override_settings(DJANGO_HTML5VALIDATOR_DIR="html_validation/test")
    def test_init_with_django_settings(self):
        """
        Test initializing with overridden settings.
        """
        validator = DjangoHTML5Validator()
        self.assertEqual(validator.report_dir, self.output_dir + "/test")
        self.assertEqual(validator.html_dir, self.output_dir + "/test/html")

    @httpretty.activate
    def test_process_response_non_html(self):
        """
        Test process_response method with non-html response content.
        """
        self.request.path = "test-process-response-non-html"
        url = "http://localhost:8000/{}".format(self.request.path)

        httpretty.register_uri(
            httpretty.GET,
            url,
            body="{}",
            content_type="json/application")

        response = requests.get(url)

        validator = DjangoHTML5Validator()
        validator.process_response(self.request, response)

        html_file = os.path.join(self.html_dir, self.request.path)
        self.assertFalse(os.path.isfile(html_file))

        reported_errors = file(self.errors_file).read()
        self.assertEqual(reported_errors, "")

    @httpretty.activate
    def test_process_response_errors(self):
        """
        Test process_response method with html response content that
        contains errors.
        """
        self.request.path = "test-process-response-with-errors"
        url = "http://localhost:8000/{}".format(self.request.path)

        httpretty.register_uri(
            httpretty.GET,
            url,
            body="<asdfghjkl></asdfghjkl>",
            content_type="text/html")

        response = requests.get(url)

        validator = DjangoHTML5Validator()
        validator.process_response(self.request, response)

        html_file = os.path.join(self.html_dir, self.request.path + ".html")
        self.assertTrue(os.path.isfile(html_file))
        self.assertAlmostEqual(os.path.getsize(self.errors_file), 765)

    @httpretty.activate
    def test_process_response_no_errors(self):
        """
        Test process_response method with html response content that
        contains no errors.
        """
        self.request.path = "test-process-response-no-errors"
        url = "http://localhost:8000/{}".format(self.request.path)

        httpretty.register_uri(
            httpretty.GET,
            url,
            body=dedent("""<!DOCTYPE html>
                <html>
                <head>
                <title>Title of the document</title>
                </head>
                <body>
                The content of the document
                </html>
            """),
            content_type="text/html")

        response = requests.get(url)

        validator = DjangoHTML5Validator()
        validator.process_response(self.request, response)

        html_file = os.path.join(self.html_dir, self.request.path + ".html")
        self.assertFalse(os.path.isfile(html_file))

        reported_errors = file(self.errors_file).read()
        self.assertEqual(reported_errors, "All good.\n")
