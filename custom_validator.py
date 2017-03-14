from eve.io.mongo import Validator
from uuid import UUID
from collections import Counter
from addresser import Addresser
import pdb

class CustomValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """
    def _validate_type_uuid(self, field, value):
        try:
            UUID(value)
        except ValueError:
            self._error(field, "value %r cannot be converted to a UUID" % value)

    def make_addresser(self):
      doc = self.document
      return Addresser(doc['num_of_rows'], doc['num_of_cols'],
          bool(doc.get('row_is_alpha')), bool(doc.get('col_is_alpha')))

    def _validate_address(self, address, field, value):
      if not address:
        return
      addresser = self.make_addresser()
      try:
        addresser.index(value)
      except ValueError as e:
        self._error(field, e.message)

    def _validate_uniqueaddresses(self, unique_addresses, field, value):
      if not unique_addresses:
        return
      c = Counter(x["address"] for x in value)

      for x, i in c.iteritems():
        if i > 1:
          self._error(field, 'Address %s is a duplicate'%x)

    def _validate_non_aker_barcode(self, non_aker_barcode, field, value):
      if not non_aker_barcode:
        return
      if self.is_new and value.upper().startswith('AKER-'):
        self._error(field, 'AKER barcode not permitted: %s'%value)

    def _validate_row_alpha_range(self, row_alpha_range, field, value):
      if row_alpha_range and self.document.get('row_is_alpha') and value > 26:
        self._error(field, 'Too many rows for alphabetical enumeration')

    def _validate_col_alpha_range(self, col_alpha_range, field, value):
      if col_alpha_range and self.document.get('col_is_alpha') and value > 26:
        self._error(field, 'Too many columns for alphabetical enumeration')

    def validate_immutable_field(self, field, data, existing):
      if (existing and data and field in data and field in existing
          and data[field]!=existing[field]):
        self._error(field, 'The %s field cannot be updated.'%field)
        return False
      return True

    # POST creating a new record
    def validate(self, *args, **kwargs):
      self.is_new = True
      return super(CustomValidator, self).validate(*args, **kwargs)

    # PUT replacing an existing record
    def validate_replace(self, document, _id, original_document=None):
      return self.validate_update(document, _id, original_document)

    # PATCH updating an existing record
    def validate_update(self, document, _id, original_document=None):
      self.is_new = False
      validated = super(CustomValidator, self).validate_update(document, _id, original_document)
      for field in 'num_of_rows num_of_cols row_is_alpha col_is_alpha barcode'.split():
        if not self.validate_immutable_field(field, document, original_document):
          validated = False
      return validated
 
