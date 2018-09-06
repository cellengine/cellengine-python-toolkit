# Copyright 2018 Primity Bio
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup, find_packages

setup(
    name="cellengine",
    version="0.1.0",  # update this in cellengine/__init__.py as well
    description="CellEngine API toolkit for Python",
    url="https://github.com/primitybio/cellengine-python-toolkit",
    author="Primity Bio",
    author_email="support@cellengine.com",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    platforms="Posix; MacOS X; Windows",
    install_requires=[
        "setuptools",
        "fcsparser==0.2.0",
        "munch==2.5.0",
        "numpy==1.17.4",
        "pandas==0.25.3",
        "python-dateutil==2.8.1",
        "requests==2.22.0",
        "requests-toolbelt==0.9.1",
        "urllib3==1.25.7",
        "custom_inherit==2.2.2",
    ],
    extras_require={"interactive": ["Pillow==7.0.0"]},
    tests_require=["pytest", "pytest-vcr"],
    python_requires=">=3.6",
    test_suite="tests.test_all",
)
