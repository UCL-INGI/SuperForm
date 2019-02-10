from setuptools import setup

setup(
    name='superform',
    packages=['superform'],
    include_package_data=True,
    install_requires=[
        'facebook-sdk',
        'feedparser',
        'flask',
        'flask-sqlalchemy',
        'requests',
        'google-api-python-client',
        'idna>=2.5,<2.8',
        'lxml',
        'oauth2client',
        'pyopenssl',
        'PyRSS2Gen',
        'pytest',
        'pytest-localserver',
        'python3-saml',
        'selenium',
        'sqlalchemy',
    ],
)
