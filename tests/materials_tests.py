import utils

from tests import MaterialsTestBase

# Using the same test framework that Eve itself uses:
# https://github.com/nicolaiarocci/eve/blob/develop/eve/tests/__init__.py
class TestMaterials(MaterialsTestBase):

  def test_material_creation(self):
    r, status = self.post(self.domain['materials']['url'], self.valid_creation_resource())

    self.assert201(status)

    self.assertRegexpMatches(r['_id'], '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')

  def test_get_empty_resource(self):
    response, status = self.get('materials')
    self.assert200(status)

    resource = response['_items']
    self.assertEqual(len(resource), 0)

    links = response['_links']
    self.assertEqual(len(links), 2)
    self.assertHomeLink(links)

  def test_material_type_required_validation(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'material_type': 'saliva' })

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'material_type': 'unallowed value saliva'})

  def test_supplier_name_required_validation(self):
    data = self.valid_creation_resource()
    del data['supplier_name']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'supplier_name': 'required field'})

  def test_donor_id_required_validation(self):
    data = self.valid_creation_resource()
    del data['donor_id']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'donor_id': 'required field'})

  def test_gender_required_validation(self):
    data = self.valid_creation_resource()
    del data['gender']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'gender': 'required field'})

  def test_gender_allowed_validation(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'gender': 'invalid' })

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'gender': 'unallowed value invalid'})

  def test_common_name_required_validation(self):
    data = self.valid_creation_resource()
    del data['common_name']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'common_name': 'required field'})

  def test_phenotype_required_validation(self):
    data = self.valid_creation_resource()
    del data['phenotype']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'phenotype': 'required field'})

  def test_meta_allows_unknown(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'meta': { 'allows': 'unknown' } })

    r, status = self.post('/materials', data=data)
    self.assert201(status)

    r, status = self.get('materials', '', r['_id'])
    self.assertEqual(r['meta']['allows'], 'unknown')

  def valid_creation_resource(self):
    return {
      "material_type": "blood",
      "supplier_name": "my supplier name 1",
      "donor_id": "my donor id 1",
      "gender": "female",
      "common_name": "Homo Sapiens",
      "phenotype": "eye colour"
    }