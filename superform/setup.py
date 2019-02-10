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
        'google-api-python-client',
        'google_auth_oauthlib',
        'idna>=2.5,<2.8',
        'lxml',
        'oauth2client',
        'pyopenssl',
        'PyRSS2Gen',
        'pytest',
        'pytest-localserver',
        'python-twitter',
        'python3-saml',
        'python3-linkedin',
        'reportlab',
        'requests',
        'rfeed',
        'selenium',
        'sqlalchemy'

    ],
)
