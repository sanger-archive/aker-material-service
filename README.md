# Materials service

A service for the creation and management of materials.

The service is written using the Eve REST API framework (which itself is based on Flask) using MongoDB as its database.

## Requirements

- Python 2.7
- pip
- virtualenv
- MongoDB

## Installation

1. Clone the repository

2. Create virtual environment `virtualenv venv`

3. Activate virtual environment `source venv/bin/activate`

4. Install the dependencies `pip install -r requirements.txt`

## Usage

Make sure MongoDB is installed and is running and that you have activated your virtual environment.

The environment variable `EVE_ENV` can be used to set the environment of the application (the default being `development` if the variable is not set). The application looks in the db directory to find a `.py` file with the name of the environment.

#### Running the server

`python run.py`

#### Running the tests

`python -m unittest discover -v -s tests -p "*tests.py"`

#### Running a single test

This runs the `single_test` test in the `TestMaterials` class in the `materials_tests` module.

`python -m unittest tests.materials_tests.TestMaterials.single_test`
