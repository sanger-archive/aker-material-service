import utils
import jwt

from tests import ServiceTestBase, valid_material_params

# Using the same test framework that Eve itself uses:
# https://github.com/nicolaiarocci/eve/blob/develop/eve/tests/__init__.py
class TestMaterials(ServiceTestBase):

  def test_material_creation(self):
    r, status = self.post(self.domain['materials']['url'], valid_material_params())

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
    data = utils.merge_dict(valid_material_params(), { 'material_type': 'saliva' })

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'material_type': 'unallowed value saliva'})

  def test_supplier_name_required_validation(self):
    data = valid_material_params()
    del data['supplier_name']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'supplier_name': 'required field'})

  def test_donor_id_required_validation(self):
    data = valid_material_params()
    del data['donor_id']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'donor_id': 'required field'})

  def test_gender_required_validation(self):
    data = valid_material_params()
    del data['gender']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'gender': 'required field'})

  def test_gender_allowed_validation(self):
    data = utils.merge_dict(valid_material_params(), { 'gender': 'invalid' })

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'gender': 'unallowed value invalid'})

  def test_common_name_required_validation(self):
    data = valid_material_params()
    del data['common_name']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'common_name': 'required field'})

  def test_phenotype_required_validation(self):
    data = valid_material_params()
    del data['phenotype']

    r, status = self.post('/materials', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(r, { 'phenotype': 'required field'})

  def test_meta_allows_unknown(self):
    data = utils.merge_dict(valid_material_params(), { 'meta': { 'allows': 'unknown' } })

    r, status = self.post('/materials', data=data)
    self.assert201(status)

    r, status = self.get('materials', '', r['_id'])
    self.assertEqual(r['meta']['allows'], 'unknown')

  def test_owner_id_is_user_when_valid_jwt(self):
    payload = {'data': { 'email': 'user@here.com', 'groups': ['pirates'] }}
    auth_token = jwt.encode(payload, 'test', algorithm='HS256')
    data = valid_material_params()

    r, status = self.post('/materials', data=data, headers=[('X-Authorisation', auth_token)])
    self.assert201(status)

    r, status = self.get('materials', '', r['_id'])
    self.assertEqual(r['owner_id'], 'user@here.com')

  def test_owner_id_is_guest_when_no_jwt(self):
    data = valid_material_params()

    r, status = self.post('/materials', data=data)
    self.assert201(status)

    r, status = self.get('materials', '', r['_id'])
    self.assertEqual(r['owner_id'], 'guest')

  def test_returns_401_when_invalid_jwt(self):
    data = valid_material_params()

    r, status = self.post('/materials', data=data, headers=[('X-Authorisation', 'jibberish.jwt.rubbish')])
    self.assert401(status)

