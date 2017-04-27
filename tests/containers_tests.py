import utils

from tests import ServiceTestBase, valid_material_params
from itertools import izip
import pdb

class TestContainers(ServiceTestBase):

  def test_container(self):
    response, status = self.get(self.domain['containers']['url'])
    self.assert200(status)

    resource = response['_items']
    self.assertEqual(len(resource), 0)

    links = response['_links']
    self.assertEqual(len(links), 2)
    self.assertHomeLink(links)

  def test_num_of_rows_min_container_creation(self):
    data = valid_container_params({ 'num_of_rows': 0 })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'num_of_rows': 'min value is 1' })

  def test_num_of_cols_min_container_creation(self):
    data = valid_container_params({ 'num_of_cols': 0 })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'num_of_cols': 'min value is 1' })

  def test_num_of_rows_max_container_creation(self):
    data = valid_container_params({ 'num_of_rows': 10000 })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'num_of_rows': 'max value is 9999' })

  def test_num_of_cols_max_container_creation(self):
    data = valid_container_params({ 'num_of_cols': 10000 })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'num_of_cols': 'max value is 9999' })

  def test_row_is_alpha_container_creation(self):
    data = valid_container_params({ 'row_is_alpha': 'yes' })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'row_is_alpha': 'must be of boolean type' })

  def test_col_is_alpha_container_creation(self):
    data = valid_container_params({ 'col_is_alpha': 'no' })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'col_is_alpha': 'must be of boolean type' })

  def test_num_of_rows_required_container_creation(self):
    data = valid_container_params()
    del data['num_of_rows']
    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'num_of_rows': 'required field' })

  def test_num_of_cols_required_container_creation(self):
    data = valid_container_params()
    del data['num_of_cols']

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'num_of_cols': 'required field' })

  def test_row_is_alpha_required_container_creation(self):
    data = valid_container_params()
    del data['row_is_alpha']

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'row_is_alpha': 'required field' })

  def test_col_is_alpha_required_container_creation(self):
    data = valid_container_params()
    del data['col_is_alpha']

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'col_is_alpha': 'required field'})

  def test_different_barcodes_are_created_when_not_provided(self):
    data = valid_container_params()

    response, status = self.post('/containers', data=data)

    self.assert201(status)

    bc1 = response['barcode']
    response, status = self.post('/containers', data=data)

    self.assert201(status)
    bc2 = response['barcode']

    self.assertTrue(bc1.startswith('AKER-'))
    self.assertTrue(bc2.startswith('AKER-'))
    self.assertNotEqual(bc1, bc2)

  def test_cannot_supply_aker_barcode(self):
    data = valid_container_params()

    response, status = self.get(self.domain['containers']['url']+'/json_schema')
    if response['properties']['barcode']['non_aker_barcode']:
      data = valid_container_params({'barcode':'aker-abc'})
      response, status = self.post('/containers', data=data)
      self.assertValidationErrorStatus(status)
      self.assertValidationError(response, { 'barcode': 'AKER barcode not permitted: aker-abc'})

  def test_barcode_is_saved_when_provided(self):
    data = valid_container_params({ 'barcode': 'xxxxxxx' })

    response, status = self.post('/containers', data=data)

    self.assert201(status)
    self.assertEqual(response['barcode'], 'xxxxxxx')

  def test_barcode_is_unique(self):
    data = valid_container_params({ 'barcode': 'xxxxxxx' })
    self.post('/containers', data=data)
    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'barcode': "value 'xxxxxxx' is not unique"})


  def test_barcode_has_min_length(self):
    data = valid_container_params({ 'barcode': 'xxx' })
    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'barcode': 'min length is'})

  def test_address_row_alpha_incorrect(self):
    materials_response, status = self.post('/materials', valid_material_params())

    data = valid_container_params({ 'slots': [
      {
        'address': '1:A',
        'material': materials_response['_id']
      }
    ] })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Invalid address format: '1:A'"})

  def test_address_col_alpha_incorrect(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'row_is_alpha': False,
      'col_is_alpha': True,
      'slots': [
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Invalid address format: 'A:1'"})

  def test_address_both_alpha_incorrect(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'row_is_alpha': True,
      'col_is_alpha': True,
      'slots': [
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Invalid address format: 'A:1'"})

  def test_address_both_numerical_incorrect(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'row_is_alpha': False,
      'col_is_alpha': False,
      'slots': [
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Invalid address format: 'A:1'"})


  def test_address_row_alpha(self):
    materials_response, status = self.post('/materials', valid_material_params())

    data = valid_container_params({
      'row_is_alpha': True,
      'col_is_alpha': False,
      'slots': [
      {
        'address': 'A:1',
        'material': materials_response['_id']
      }
    ] })

    response, status = self.post('/containers', data=data)
    self.assert201(status)

  def test_address_col_alpha(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'row_is_alpha': False,
      'col_is_alpha': True,
      'slots': [
        {
          'address': '1:A',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assert201(status)

  def test_address_both_alpha(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'row_is_alpha': True,
      'col_is_alpha': True,
      'slots': [
        {
          'address': 'A:A',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assert201(status)

  def test_address_both_numerical(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'row_is_alpha': False,
      'col_is_alpha': False,
      'slots': [
        {
          'address': '1',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assert201(status)

  def test_out_of_range_row(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'slots': [
        {
          'address': 'I:12',
          'material': materials_response['_id'],
        }
      ]
      })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Row out of range: 'I:12'"})

  def test_out_of_upper_range_col(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'slots': [
        {
          'address': 'H:13',
          'material': materials_response['_id'],
        }
      ]
      })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Column out of range: 'H:13'"})

  def test_out_of_lower_range_col(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'slots': [
        {
          'address': 'H:0',
          'material': materials_response['_id'],
        }
      ]
      })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Column out of range: 'H:0'"})

  def test_out_of_range_both_numeric(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'row_is_alpha' : False,
      'slots': [
        {
          'address': '97',
          'material': materials_response['_id'],
        }
      ]
      })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Address out of range: '97'"})

  def test_out_of_lower_range_address(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'row_is_alpha' : False,
      'slots': [
        {
          'address': '0',
          'material': materials_response['_id'],
        }
      ]
      })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertEqual(response['_issues']['slots']['0'], {'address': "Address out of range: '0'"})

  def test_multiple_addresses_all_duplicates(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'slots': [
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        },
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'slots': "Address A:1 is a duplicate"})

  def test_multiple_addresses_some_duplicates(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'slots': [
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        },
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        },
        {
          'address': 'E:5',
          'material': materials_response['_id'],
        },
        {
          'address': 'E:5',
          'material': materials_response['_id'],
        },
        {
          'address': 'F:7',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'slots': "Address A:1 is a duplicate"})
    self.assertValidationError(response, { 'slots': "Address E:5 is a duplicate"})
    self.assertEqual(len(response['_issues']['slots']), 2)

  def test_multiple_addresses_no_duplicates(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'slots': [
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        },
        {
          'address': 'B:2',
          'material': materials_response['_id'],
        },
        {
          'address': 'C:3',
          'material': materials_response['_id'],
        }
      ]
    })
    response, status = self.post('/containers', data=data)
    self.assert201(status)

  def test_materials_can_be_embedded(self):
    materials_response, status = self.post('/materials', valid_material_params())
    data = valid_container_params({
      'slots': [
        {
          'address': 'A:1',
          'material': materials_response['_id'],
        }
      ]
    })

    container, _ = self.post('/containers', data=data)

    response, status = self.get('containers/' + container['_id'] + '?embedded={"slots.material": 1}')

    self.assert200(status)

    del materials_response['_links']
    del materials_response['_status']

    self.assertEqual(response['slots'][0]['material'], materials_response)

  def test_row_alpha_range(self):
    data = valid_container_params({
      'row_is_alpha': True,
      'num_of_rows': 27,
    })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'num_of_rows': 'Too many rows for alphabetical enumeration'})

  def test_column_alpha_range(self):
    data = valid_container_params({
      'col_is_alpha': True,
      'num_of_cols': 27,
    })
    response, status = self.post('/containers', data=data)
    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'num_of_cols': 'Too many columns for alphabetical enumeration'})

  def test_column_numerical_range(self):
    data = valid_container_params({
      'row_is_alpha': False,
      'col_is_alpha': False,
      'num_of_rows': 27,
      'num_of_cols': 27,
    })
    response, status = self.post('/containers', data=data)
    self.assert201(status)

  def test_plate_with_no_slots_has_slots_added_row_alpha(self):
    data = valid_container_params({
      'row_is_alpha': True,
      'col_is_alpha': False,
      'num_of_rows': 2,
      'num_of_cols': 3,
      })
    expectedaddresses = 'A:1 A:2 A:3 B:1 B:2 B:3'.split()
    response, status = self.post('/containers', data=data)
    self.assert201(status)
    slots = response['slots']
    self.assertEqual(len(slots), len(expectedaddresses))
    for slot, ad in izip(slots, expectedaddresses):
      self.assertEqual(slot.get('material'), None)
      self.assertEqual(slot.get('address'), ad)

  def test_plate_with_no_slots_has_slots_added_col_alpha(self):
    data = valid_container_params({
      'row_is_alpha': False,
      'col_is_alpha': True,
      'num_of_rows': 2,
      'num_of_cols': 3,
      })
    expectedaddresses = '1:A 1:B 1:C 2:A 2:B 2:C'.split()
    response, status = self.post('/containers', data=data)
    self.assert201(status)
    slots = response['slots']
    self.assertEqual(len(slots), len(expectedaddresses))
    for slot, ad in izip(slots, expectedaddresses):
      self.assertEqual(slot.get('material'), None)
      self.assertEqual(slot.get('address'), ad)

  def test_plate_with_no_slots_has_slots_added_numeric(self):
    data = valid_container_params({
      'row_is_alpha': False,
      'col_is_alpha': False,
      'num_of_rows': 2,
      'num_of_cols': 3,
      })
    expectedaddresses = map(str, range(1,7))
    response, status = self.post('/containers', data=data)
    self.assert201(status)
    slots = response['slots']
    self.assertEqual(len(slots), len(expectedaddresses))
    for slot, ad in izip(slots, expectedaddresses):
      self.assertEqual(slot.get('material'), None)
      self.assertEqual(slot.get('address'), ad)

  def test_plate_with_some_slots_has_empty_slots_added(self):
    materials_response, status = self.post('/materials', valid_material_params())
    material_id = materials_response['_id']
    data = valid_container_params({
      'row_is_alpha': True,
      'col_is_alpha': False,
      'num_of_rows': 2,
      'num_of_cols': 3,
      'slots': [
        {
          'address': 'A:1',
          'material': material_id,
        }
      ]
    })
    container, _ = self.post('/containers', data=data)

    response, status = self.get('containers/%s?embedded={"slots.material": 1}'%container['_id'])

    self.assert200(status)
    slots = response['slots']
    self.assertEqual(len(slots), 6)
    expectedaddresses = 'A:1 A:2 A:3 B:1 B:2 B:3'.split()
    for slot, address in izip(slots, expectedaddresses):
      self.assertEqual(slot['address'], address)
      if address=='A:1':
        self.assertEqual(slot['material']['_id'], material_id)
      else:
        self.assertEqual(slot.get('material'), None)

  def test_update_plate_without_giving_barcode(self):
    data = valid_container_params()
    response, status = self.post('/containers', data=data)
    self.assert201(status)
    plateid = response['_id']
    update = { 'print_count': 17 }
    _, status = self.patch('/containers/%s'%plateid, data=update)
    self.assert200(status)

  def test_update_immutable_fields(self):
    data = valid_container_params()
    response, status = self.post('/containers', data=data)
    self.assert201(status)
    plateid = response['_id']
    update = { 'barcode': 'COLORADO', 'num_of_rows':100, 'col_is_alpha':True }
    response, status = self.patch('/containers/%s'%plateid, data=update)
    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'barcode': 'The barcode field cannot be updated'})
    self.assertValidationError(response, { 'num_of_rows': 'The num_of_rows field cannot be updated'})
    self.assertValidationError(response, { 'col_is_alpha': 'The col_is_alpha field cannot be updated'})

  def test_update_plate_with_same_barcode(self):
    data = valid_container_params()
    response, status = self.post('/containers', data=data)
    self.assert201(status)
    plateid = response['_id']
    barcode = response['barcode']
    update = { 'print_count': 17, 'barcode': barcode }
    _, status = self.patch('/containers/%s'%plateid, data=update)
    self.assert200(status)
    # Some variations of this test fell foul of https://github.com/pyeve/eve/issues/920
    # -- a bug about patch requests raising a 412

# helper

def valid_container_params(changes=None):
  d = {
      'num_of_rows': 8,
      'num_of_cols': 12,
      'row_is_alpha': True,
      'col_is_alpha': False
    }
  if changes:
    d.update(changes)
  return d
