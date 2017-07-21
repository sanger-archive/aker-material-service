import os
import sys

from flask import current_app
from flask_pymongo import MongoClient
from eve.tests import TestMinimal
from run import create_app

sys.path.insert(0, os.path.abspath('../db'))

from db.test import MONGO_HOST, MONGO_PORT, MONGO_DBNAME

SETTINGS_PATH = os.path.join(os.path.dirname('..'), 'db', 'test.py')

class ServiceTestBase(TestMinimal):

  def setUp(self, settings_file=None, url_converters=None):

    self.this_directory = os.path.dirname(os.path.realpath(__file__))

    if settings_file is None:
      settings_file = SETTINGS_PATH

    self.connection = None
    self.setupDB()

    self.settings_file = settings_file
    self.app = create_app(SETTINGS_PATH)
    self.app.testing = True

    self.test_client = self.app.test_client()

    self.domain = self.app.config['DOMAIN']

  def setupDB(self):
    self.connection = MongoClient(MONGO_HOST, MONGO_PORT)

  def tearDown(self):
    with self.app.app_context():
      current_app.data.driver.db.materials.remove({})
      current_app.data.driver.db.containers.remove({})
    del self.app

def valid_material_params():
  return {
    "material_type": "blood",
    "supplier_name": "my supplier name 1",
    "donor_id": "my donor id 1",
    "gender": "female",
    "scientific_name": "Homo Sapiens",
    "phenotype": "eye colour"
  }