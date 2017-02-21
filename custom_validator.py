from eve.io.mongo import Validator
from uuid import UUID
from collections import Counter

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

    def _validate_address(self, address, field, value):
      if not address:
        return
      ad = self.parse_address(value)
      if ad is None:
        self._error(field, '%s is in the incorrect format'%value)
        return
      num_rows = self.document['num_of_rows']
      num_cols = self.document['num_of_cols']
      if isinstance(ad, tuple):
        r, c = ad
        if not 1<=r<=num_rows:
          self._error(field, 'Row out of range in %s'%value)
        if not 1<=c<=num_cols:
          self._error(field, 'Column out of range in %s'%value)
      else:
        if not 1<=ad<=num_rows*num_cols:
          self._error(field, 'Address out of range in %s'%value)


    def parse_address(self, address):
      row_alpha = self.document.get('row_is_alpha')
      col_alpha = self.document.get('col_is_alpha')
      if row_alpha or col_alpha:
        if ':' not in address:
          return None
        r,c = address.split(':')
        row_index = self.address_value(r, row_alpha)
        col_index = self.address_value(c, col_alpha)
        if None in (row_index, col_index):
          return None
        return row_index, col_index
      if not address.isdigit():
        return None
      return int(address)

    def address_value(self, value, alpha):
      if alpha:
        if not 'A'<=value<='Z':
          return None
        return ord(value)-ord('A')+1
      else:
        if not value.isdigit():
          return None
        return int(value)

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

