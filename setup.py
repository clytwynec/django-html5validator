from setuptools import setup, find_packages

setup(
    name='django-html5validator',
    version = "0.0.1",
    packages = find_packages(exclude=['tests', 'tests.*']),
    license='Apache 2.0',
    install_requires = [
        'django',
        'html5validator==0.1.14',
    ],
    # metadata for upload to PyPI
    author = "Christine Lytwynec",
    author_email = "chris.lytwynec@gmail.com",
    description = "Middleware to store invalid html and errors from html5validator",
)
