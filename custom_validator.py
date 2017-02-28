from eve.io.mongo import Validator
from uuid import UUID
from collections import Counter
from addresser import Addresser

class CustomValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """
    def _validate_type_uuid(self, field, value):
        try:
            UUID(value)
        except ValueError:
            self._error(field, "value %r cannot be converted to a UUID" %
                        value)

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
      if value.upper().startswith('AKER-'):
        self._error(field, 'AKER barcode not permitted: %s'%value)

    def _validate_row_alpha_range(self, row_alpha_range, field, value):
      if row_alpha_range and self.document.get('row_is_alpha') and value > 26:
        self._error(field, 'Too many rows for alphabetical enumeration')

    def _validate_col_alpha_range(self, col_alpha_range, field, value):
      if col_alpha_range and self.document.get('col_is_alpha') and value > 26:
        self._error(field, 'Too many columns for alphabetical enumeration')

