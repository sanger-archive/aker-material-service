import os

ENVIRONMENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'environment.py')
execfile(ENVIRONMENT_PATH)

material_type_schema = {
  'name': {
    'type': 'string',
    'required': True
  }
}

material_schema = {
    'material_type': {
      'type': 'objectid',
      'data_relation': {
        'resource': 'material_types',
        'field': '_id',
        'embeddable': True
      }
    },
    'supplier_name': {
      'type': 'string',
    },
    'donor_id': {
      'type': 'string',
    },
    'gender': {
      'type': 'string',
      'allowed': ['male', 'female', 'unknown'],
      'required': True
    },
    'common_name': {
      'type': 'string',
    },
    'phenotype': {
      'type': 'string',
    },
    'date_of_receipt': {
      'type': 'datetime',
    },
    'meta': {
      'type': 'dict',
      'allow_unknown': True,
    },
    'ancestors': {
      'type': 'list',
      'schema': {
        'type': 'objectid',
        'data_relation': {
          'resource': 'materials',
          'field': '_id',
          'embeddable': True
        }
      },
    },
    'parent': {
      'type': 'objectid'
    }
}

material_types = {
  'schema': material_type_schema
}

materials = {
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'schema': material_schema
}

DOMAIN = {
  'materials': materials,
  'material_types': material_types
}