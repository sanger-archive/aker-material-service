def index_to_address_part(index, alpha):
    """Return the row/column part of an address using the given index (from zero),
    either 0->"A", 1->"B" or 0->"1", 1->"2", ...
    """
    if alpha:
        return chr(ord('A')+index)
    else:
        return str(index+1)


def address_part_to_index(part, alpha):
    """Convert the letter or number from part of an address to a zero-based index.
    Return None if the conversion is impossible.
    """
    if alpha:
        if 'A' <= part <= 'Z':
            return ord(part)-ord('A')
    else:
        if part.isdigit():
            return int(part)-1


class Addresser(object):
    """Class for converting to/from container slot addresses."""

    def __init__(self, num_rows, num_cols, row_is_alpha, col_is_alpha, separator=':'):
        """Initialise the addresser with given dimensions and conversion rules."""
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.row_is_alpha = row_is_alpha
        self.col_is_alpha = col_is_alpha
        self.separator = separator

    def __len__(self):
        return self.num_rows*self.num_cols

    @property
    def is_numeric(self):
        return not (self.col_is_alpha or self.row_is_alpha)

    def index_to_address(self, index):
        """Convert the given index to an address."""
        if not 0 <= index < len(self):
            raise IndexError("Index out of address range: %s", index)
        if self.is_numeric:
            return str(index+1)
        row = index//self.num_cols
        col = index % self.num_cols
        return self.separator.join([
            index_to_address_part(i, a)
            for i, a in ((row, self.row_is_alpha), (col, self.col_is_alpha))
        ])

    __getitem__ = index_to_address

    def __contains__(self, address):
        """Is the given address valid for this addresser?"""
        if self.is_numeric:
            return address.isdigit() and 1 <= int(address) <= len(self)
        if self.separator not in address:
            return False
        r, c = address.split(self.separator, 1)
        ri, ci = (address_part_to_index(i, a)
                  for i, a in ((r, self.row_is_alpha), (c, self.col_is_alpha)))
        return (ri is not None and ci is not None
                and 0 <= ri < self.num_rows and 0 <= ci < self.num_cols)

    def index(self, address):
        """Convert the given address (a string) to a 0-based index.
        Raises a ValueError if the address cannot be converted."""
        if isinstance(address, unicode):
            address = str(address)
        elif not isinstance(address, str):
            raise TypeError("Address must be a string")

        if self.is_numeric:
            if not address.isdigit():
                raise ValueError("Invalid address format: %r" % address)
            i = int(address)-1
            if not 0 <= i < len(self):
                raise ValueError("Address out of range: %r" % address)
            return i

        if self.separator not in address:
            ri = ci = None
        else:
            r, c = address.split(self.separator, 1)
            ri, ci = (address_part_to_index(i, a)
                      for i, a in ((r, self.row_is_alpha), (c, self.col_is_alpha)))
        if ri is None or ci is None:
            raise ValueError("Invalid address format: %r" % address)
        if not 0 <= ri < self.num_rows:
            if not 0 <= ci < self.num_cols:
                raise ValueError("Row and column out of range: %r" % address)
            raise ValueError("Row out of range: %r" % address)
        if not 0 <= ci < self.num_cols:
            raise ValueError("Column out of range: %r" % address)
        return ri*self.num_cols + ci

    def __repr__(self):
        return 'Addresser(num_rows=%s, num_cols=%s, row_is_alpha=%s, col_is_alpha=%s)' % (
               self.num_rows, self.num_cols, self.row_is_alpha, self.col_is_alpha
        )
