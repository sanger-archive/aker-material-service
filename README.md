# Aker - Materials service

[![Build Status](https://travis-ci.org/sanger/aker-material-service.svg?branch=devel)](https://travis-ci.org/sanger/aker-material-service)
[![Maintainability](https://api.codeclimate.com/v1/badges/260ee8cfb2ee2d64dc32/maintainability)](https://codeclimate.com/github/sanger/aker-material-service/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/260ee8cfb2ee2d64dc32/test_coverage)](https://codeclimate.com/github/sanger/aker-material-service/test_coverage)

A service for the creation and management of materials.

The service is written using the [Eve](http://python-eve.org/index.html) REST
API framework (which itself is based on Flask) using MongoDB as its database.

## Requirements

- Python 2.7.15
- pip
- virtualenv
- MongoDB

## Installation

1. Clone the repository

2. Create virtual environment `virtualenv venv`

3. Activate virtual environment `source venv/bin/activate`

4. Install the dependencies `pip install -r requirements.txt`

## Usage

Make sure MongoDB is installed and is running and that you have activated your
virtual environment.

The environment variable `EVE_ENV` can be used to set the environment of the
application (the default being `development` if the variable is not set). The
application looks in the db directory to find a `.py` file with the name of the
environment.

### Running the server

`python run.py`

#### Running the tests

`python -m unittest discover -v -s tests -p "*tests.py"`

#### Running a single test

This runs the `single_test` test in the `TestMaterials` class in the
`materials_tests` module.

`python -m unittest tests.materials_tests.TestMaterials.single_test`

## Misc.
### Linting
A `setup.cfg` exists for the `pycodestyle` linting package and can be used by installing it via
pip: `pip install pycodestyle`. Once it's installed, it can be used via the command-line or an IDE
package.
