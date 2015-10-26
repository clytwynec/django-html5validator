"""
Tests for the middleware
"""
import httpretty
import os
import requests
import time

from django.conf import settings
from django.test.utils import override_settings
from django_html5validator.middleware import DjangoHTML5Validator
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

LONG_FILENAME = "abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghij"\
    "1abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "2abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "3abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "4abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "5abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "6abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "7abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "8abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "9abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstuv"\
    "10abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstu"\
    "11abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstu"\
    "12abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnopqrstu"\
    "13abcd-efghijkl.html"\

TRUNCATED_FILENAME = "abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-e"\
    "fghij1abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmnop"\
    "qrstuv2abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmno"\
    "pqrstuv3abcd-efghijklmnopqrstuv-wxyz-12345-6-7-89-abcd-efghijklmn"\
    "opqrstu.html"


class MockRequest(object):
    path = ""


class DjangoHTML5ValidatorTestCase(TestCase):
    """
    Unit tests for the DjangoHTML5Validator middleware.
    """
    def setUp(self):
        self.output_dir = "html_validation"
        self.html_dir = os.path.join(self.output_dir, "html")
        self.errors_file = os.path.join(self.output_dir, "errors.txt")

        self.addCleanup(rmtree, self.output_dir, ignore_errors=True)
        self.request = MockRequest()

    def wait_for_validation(self, validator):
        timeout = 30
        while timeout > 0:
            time.sleep(1)
            timeout -=1
            if validator.job_complete:
                return
        raise Exception("Timed out waiting for html validation.")

    def test_init_default(self):
        # Test initializing with default settings.
        validator = DjangoHTML5Validator()
        self.assertEqual(validator.report_dir, self.output_dir)
        self.assertEqual(validator.html_dir, self.html_dir)

    @override_settings(DJANGO_HTML5VALIDATOR_DIR="html_validation/test")
    def test_init_with_django_settings(self):
        # Test initializing with overridden settings.
        validator = DjangoHTML5Validator()
        self.assertEqual(validator.report_dir, self.output_dir + "/test")
        self.assertEqual(validator.html_dir, self.output_dir + "/test/html")

    @httpretty.activate
    def test_process_response_non_html(self):
        # Test process_response method with non-html response content.
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
        # self.wait_for_validation(validator)
        self.assertFalse(os.path.isfile(validator.html_file_path))

        reported_errors = file(self.errors_file).read()
        self.assertEqual(reported_errors, "")

    @httpretty.activate
    def test_process_response_errors(self):
        # Test process_response method with html response content that
        # contains errors.
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
        self.wait_for_validation(validator)

        self.assertTrue(os.path.isfile(validator.html_file_path))
        reported_errors = file(self.errors_file).read()
        self.assertIn(
            "error: Start tag seen without seeing a doctype first",
            reported_errors
        )

    @httpretty.activate
    def test_process_response_long_filename(self):
        # Test process_response method with a file path that needs to
        # be truncated.
        self.request.path = LONG_FILENAME
        url = "http://localhost:8000/{}".format(self.request.path)

        httpretty.register_uri(
            httpretty.GET,
            url,
            body="<asdfghjkl></asdfghjkl>",
            content_type="text/html")

        response = requests.get(url)

        validator = DjangoHTML5Validator()
        validator.process_response(self.request, response)
        self.wait_for_validation(validator)
        self.assertTrue(os.path.isfile(validator.html_file_path))

    @httpretty.activate
    def test_process_response_no_errors(self):
        # Test process_response method with html response content that
        # contains no errors.
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
        self.wait_for_validation(validator)

        self.assertFalse(os.path.isfile(validator.html_file_path))

        reported_errors = file(self.errors_file).read()
        self.assertEqual(reported_errors, "All good.\n")
