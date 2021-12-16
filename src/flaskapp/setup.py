import sys

from setuptools import setup, find_packages


setup(
    version='0.1',
    name='face_api_flask',
    package_dir={'': 'face_api'},
    packages=find_packages(where='face_api'),
    install_requires=[
        'flask',
        'gunicorn'
    ],
)
