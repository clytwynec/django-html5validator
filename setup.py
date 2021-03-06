from setuptools import setup, find_packages

setup(
    name='django-html5validator',
    version = "0.0.1",
    url='http://github.com/clytwynec/django-html5validator',
    packages = find_packages(exclude=['tests', 'tests.*']),
    license='Apache 2.0',
    install_requires = [
        'APScheduler>=3.0.4',
        'django',
        'html5validator',
        'python-slugify>=1.1.4',
    ],
    dependency_links=[
        "git+https://github.com/clytwynec/html5validator.git@master#egg=html5validator",
    ],
    # metadata for upload to PyPI
    author = "Christine Lytwynec",
    description = "Django middleware to check html validity using html5validator",
)
