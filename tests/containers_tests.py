import utils

from tests import ServiceTestBase

class TestContainers(ServiceTestBase):

  def test_container(self):
    response, status = self.get(self.domain['containers']['url'])
    self.assert200(status)

    resource = response['_items']
    self.assertEqual(len(resource), 0)

    links = response['_links']
    self.assertEqual(len(links), 2)
    self.assertHomeLink(links)

  def test_x_size_min_container_creation(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'x_size': 0 })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'x_size': 'min value is 1' })

  def test_y_size_min_container_creation(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'y_size': 0 })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'y_size': 'min value is 1' })

  def test_x_size_max_container_creation(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'x_size': 10000 })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'x_size': 'max value is 9999' })

  def test_y_size_max_container_creation(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'y_size': 10000 })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'y_size': 'max value is 9999' })

  def test_x_is_alpha_container_creation(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'x_is_alpha': 'yes' })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'x_is_alpha': 'must be of boolean type' })

  def test_y_is_alpha_container_creation(self):
    data = utils.merge_dict(self.valid_creation_resource(), { 'y_is_alpha': 'no' })

    response, status = self.post('/containers', data=data)

    self.assertValidationErrorStatus(status)
    self.assertValidationError(response, { 'y_is_alpha': 'must be of boolean type' })

  def valid_creation_resource(self):
    return {
      'x_size': 12,
      'y_size': 8,
      'x_is_alpha': True,
      'y_is_alpha': False
    }