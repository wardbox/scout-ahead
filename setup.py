try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'scout-ahead is a drafting tool for league of legends',
    'author': 'wardbox',
    'url': '',
    'download_url': '',
    'author_email': 'dylan.kappler@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['scout-ahead'],
    'scripts': [],
    'name': 'scout-ahead'
}

setup(**config)