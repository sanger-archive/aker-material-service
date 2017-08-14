# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

# Disables concurrency control
# When enabled, ETag is required value within If-Match HTTP header
# Stops race conditions (which we'll ignore for now for testing purposes)
IF_MATCH = False

ITEM_URL = 'regex("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}")'

BANDWIDTH_SAVER = False

SWAGGER_INFO = {
  'title': 'Materials Service',
  'description': 'A RESTful web service for storing material data',
  'version': 'v1'
}

material_schema = {
  '_id': {
    'type': 'uuid'
  },
  'material_type': {
    'type': 'string',
    'allowed': ['blood', 'dna']
  },
  'available': {
    'type': 'boolean',
    'required': False,
    'default': False
  },
  'supplier_name': {
    'type': 'string',
    'required': True
  },
  'donor_id': {
    'type': 'string',
    'required': True
  },
  'gender': {
    'type': 'string',
    'allowed': ['male', 'female', 'unknown'],
    'required': True
  },
  'scientific_name': {
    'type': 'string',
    'required': True,
    'allowed': ['Homo sapiens', 'Mus musculus']
  },
  'phenotype': {
    'type': 'string',
    'required': True,
  },
  'hmdmc': {
    'type': 'string',
    'required': False,
    'hmdmc_format': True,
  },
  'hmdmc_not_required_confirmed_by': {
    'type': 'string',
    'required': False,
    'not_blank': True,
  },
  'hmdmc_set_by': {
    'type': 'string',
    'required': False,
    'required_with_hmdmc': True,
    'not_blank': True,
  },
  'date_of_receipt': {
    'type': 'datetime',
  },
  'owner_id': {
    'type': 'string'
  },
  'meta': {
    'type': 'dict',
    'allow_unknown': True,
  },
  'ancestors': {
    'type': 'list',
    'schema': {
      'type': 'uuid',
      'data_relation': {
        'resource': 'materials',
        'field': '_id',
        'embeddable': True
      }
    },
  },
  'parents': {
    'type': 'list',
    'schema': {
      'type': 'uuid',
      'data_relation': {
        'resource': 'materials',
        'field': '_id',
        'embeddable': True
      }
    },
  }
}

container_schema = {
  '_id': {
    'type': 'uuid'
  },
  'num_of_rows': {
    'type': 'integer',
    'min': 1,
    'max': 9999,
    'required': True,
    'row_alpha_range': True
  },
  'num_of_cols': {
    'type': 'integer',
    'min': 1,
    'max': 9999,
    'required': True,
    'col_alpha_range': True
  },
  'print_count': {
    'type': 'integer',
    'min': 0,
    'max': 9999,
    'required': False
  },
  'row_is_alpha': {
    'type': 'boolean',
    'required': True
  },
  'col_is_alpha': {
    'type': 'boolean',
    'required': True
  },
  'barcode': {
    'type': 'string',
    'unique': True,
    'minlength': 6,
    'non_aker_barcode': True,
  },
  'slots': {
    'type': 'list',
    'uniqueaddresses': True,
    'schema': {
      'type': 'dict',
      'schema': {
        'address': { 'type': 'string', 'address': True },
        'material': {
          'type': 'uuid',
          'data_relation': {
            'resource': 'materials',
            'field': '_id',
            'embeddable': True
          }
        }
      }
    }
  }
}

DOMAIN = {
  'materials': {
    'schema': material_schema
  },
  'containers': {
    'schema': container_schema
  }
}
