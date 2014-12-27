__author__ = 'matias'

from setuptools import setup, find_packages

setup(
    name="Kea",
    version="0.0.0",
    author='Kodemates',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'kea = kea.main:main',
        ]
    }
)
