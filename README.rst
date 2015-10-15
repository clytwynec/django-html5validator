Installation
------------

.. code:: bash

    pip install django-html5validator


Setup
-----

To add the DjangoHTML5Validator middleware class to the python settings file:

.. code:: python

    MIDDLEWARE_CLASSES += ('django_html5validator.middleware.DjangoHTML5Validator',)


Optionally, specify a directory to put the output of the html
validation in. By default, the output will be put in a folder
called ``html_validation`` in the working directory. For example:

.. code:: python

    DJANGO_HTML5VALIDATOR_DIR = REPORTS_DIR / "html_validation"
