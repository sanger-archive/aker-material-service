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


    def test_material_with_parents_creation(self):
        r1, status1 = self.post(self.domain['materials']['url'], valid_material_params())
        self.assert201(status1)
        r2, status2 = self.post(self.domain['materials']['url'], valid_material_params())
        self.assert201(status2)

        params = valid_material_params()
        params['parents'] = [r1['_id'], r2['_id']]
        r, status = self.post(self.domain['materials']['url'], params)
        self.assert201(status)

        self.assertRegexpMatches(r['_id'], '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')

    def test_material_with_wrong_parents_not_created(self):
        import uuid

        r1, status1 = self.post(self.domain['materials']['url'], valid_material_params())
        self.assert201(status1)

        params = valid_material_params()
        params['parents'] = [r1['_id'], str(uuid.uuid4())]
        r, status = self.post(self.domain['materials']['url'], params)
        self.assert422(status)


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

    def test_scientific_name_required_validation(self):
        data = valid_material_params()
        del data['scientific_name']

        r, status = self.post('/materials', data=data)

        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, { 'scientific_name': 'required field'})

    def test_phenotype_required_validation(self):
        data = valid_material_params()
        del data['phenotype']

        r, status = self.post('/materials', data=data)

        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, { 'phenotype': 'required field'})

    def test_hmdmc_invalid_format(self):
        data = valid_material_params()
        data['hmdmc'] = '12345'
        data['hmdmc_set_by'] = 'a@b.c'

        r, status = self.post('/materials', data=data)

        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'hmdmc': 'format'})

    def test_hmdmc_blank(self):
        data = valid_material_params()
        data['hmdmc'] = ''
        data['hmdmc_set_by'] = 'a@b.c'

        r, status = self.post('/materials', data=data)

        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'hmdmc': 'format'})


    def test_hmdmc_missing_set_by(self):
        data = valid_material_params()
        data['hmdmc'] = '12/345'
        r, status = self.post('/materials', data=data)
        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'hmdmc_set_by': 'hmdmc'})

    def test_hmdmc_with_set_by(self):
        data = valid_material_params()
        data['hmdmc'] = '12/345'
        data['hmdmc_set_by'] = 'a@b.c'
        r, status = self.post('/materials', data=data)
        self.assert201(status)

    def test_hmdmc_with_blank_set_by(self):
        data = valid_material_params()
        data['hmdmc'] = '12/345'
        data['hmdmc_set_by'] = ' '
        r, status = self.post('/materials', data=data)
        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'hmdmc_set_by': 'blank'})

    def test_hmdmc_with_spaces_set_by(self):
        data = valid_material_params()
        data['hmdmc'] = '12/345'
        data['hmdmc_set_by'] = '  '
        r, status = self.post('/materials', data=data)
        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'hmdmc_set_by': 'blank'})

    def test_hmdmc_not_required_confirmed_by_blank(self):
        data = valid_material_params()
        data['hmdmc_not_required_confirmed_by']=''
        r, status = self.post('/materials', data=data)
        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'hmdmc_not_required_confirmed_by': 'blank'})

    def test_available(self):
        data = valid_material_params()
        r1, status = self.post('/materials', data=data)
        self.assert201(status)
        self.assertEqual(r1['available'], False) # should be False, not None
        r2, status = self.patch('/materials/'+r1['_id'], data={ 'available': True })
        self.assert200(status)
        self.assertEqual(r2['available'], True)

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

    def test_verify_ownership_422_missing_owner_id(self):
        materials_data = utils.merge_dict(valid_material_params(), { 'owner_id': 'abc' })
        r, _ = self.post('/materials', data=materials_data)

        data = { 'materials': [r['_id']] }

        r, status = self.post('/materials/verify_ownership', data=data)
        self.assert422(status)

    def test_verify_ownership_422_missing_materials(self):
        data = { 'owner_id': 'cs24@sanger.ac.uk' }

        r, status = self.post('/materials/verify_ownership', data=data)
        self.assert422(status)

    def test_verify_ownership_422_empty_materials(self):
        data = { 'owner_id': 'cs24@sanger.ac.uk', 'materials': [] }

        r, status = self.post('/materials/verify_ownership', data=data)
        self.assert200(status)

    def test_verify_ownership_materials_belong_to_owner_id(self):
        materials_data = utils.merge_dict(valid_material_params(), { 'owner_id': 'abc' })

        r1, _ = self.post('/materials', data=materials_data)
        r2, _ = self.post('/materials', data=materials_data)
        r3, _ = self.post('/materials', data=materials_data)

        data = { 'owner_id': 'abc', 'materials': [r1['_id'], r2['_id'], r3['_id']] }

        r, status = self.post('/materials/verify_ownership', data=data)
        self.assert200(status)

    def test_verify_ownership_materials_dont_belong_to_ownerid(self):
        abc_materials_data = utils.merge_dict(valid_material_params(), { 'owner_id': 'abc' })
        xyz_materials_data = utils.merge_dict(valid_material_params(), { 'owner_id': 'xyz' })

        r1, _ = self.post('/materials', data=abc_materials_data)
        r2, _ = self.post('/materials', data=abc_materials_data)
        r3, _ = self.post('/materials', data=xyz_materials_data)

        abc_materials = [r1['_id'], r2['_id']]
        xyz_materials = [r3['_id']]

        data = { 'owner_id': 'xyz', 'materials': abc_materials + xyz_materials }

        r, status = self.post('/materials/verify_ownership', data=data)

        self.assert403(status)
        self.assertEqual(len(r['_issues']), 2)

    def test_bulk_search_materials(self):
        query = { 'owner_id': 'abc'}
        query_empty = { 'owner_id': 'xyz'}
        abc_materials_data = utils.merge_dict(valid_material_params(), query)
        r1, _ = self.post('/materials', data=abc_materials_data)

        r, status = self.post('/materials/search', data={'where': query})

        self.assert200(status)
        self.assertEqual(len(r['_items']), 1)

        r, status = self.post('/materials/search', data={'where': query_empty})

        self.assert200(status)
        self.assertEqual(len(r['_items']), 0)        
