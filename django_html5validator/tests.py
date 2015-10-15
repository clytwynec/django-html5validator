"""
Tests for the middleware
"""
import os

from django.conf import settings
from django.test.utils import override_settings
from middleware import DjangoHTML5Validator
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
        self.response = Mock()

    def test_init_default(self):
        validator = DjangoHTML5Validator()
        self.assertEqual(validator.report_dir, self.output_dir)
        self.assertEqual(validator.html_dir, self.html_dir)

    @override_settings(DJANGO_HTML5VALIDATOR_DIR="html_validation/test")
    def test_init_with_django_settings(self):
        validator = DjangoHTML5Validator()
        self.assertEqual(validator.report_dir, self.output_dir + "/test")
        self.assertEqual(validator.html_dir, self.output_dir + "/test/html")

    def test_process_response_non_html(self):
        self.request.path = "test_process_response_non_html"
        self.response = {"content-type": "json/application"}
        validator = DjangoHTML5Validator()
        validator.process_response(self.request, self.response)

        html_file = os.path.join(self.html_dir, self.request.path)
        self.assertFalse(os.path.isfile(html_file))
        self.assertAlmostEqual(os.path.getsize(self.errors_file), 0)

    # def test_process_response_html_with_errors(self):
    #     # TODO
    #     pass

    # def test_process_response_html_no_errors(self):
    #     # TODO
    #     pass

