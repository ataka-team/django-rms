from setuptools import setup, find_packages

version = "0.0.0"

long_description=""
try:
    long_description=file('README').read()
except Exception:
    pass

license=""
try:
    license=file('MIT_License.txt').read()
except Exception:
    pass

setup(
    name = 'django-rms',
    version = version,
    description = 'Django Rule Management System app',
    author = 'Pablo Saavedra',
    author_email = 'pablo.saavedra@treitos.com',
    url = 'http://github.com/psaavedra/django-rms',
    download_url= 'https://github.com/psaavedra/django-rms/zipball/master',
    packages = find_packages(),
    package_data={
        'rms': [
            'templates/admin/rms/application/*.html',
            'static/*/css/*.css',
            'static/*/img/*',
            'static/*/js/*.js',
        ],
    },

    zip_safe=False,
    install_requires=[
        "django",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=long_description,
    license=license,
    keywords = "rule manager django rms",
)
