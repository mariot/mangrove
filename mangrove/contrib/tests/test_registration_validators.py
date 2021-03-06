
import unittest
from mock import Mock, patch
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.validator_factory import validator_factory
from mangrove.form_model.validator_types import ValidatorTypes
from mangrove.form_model.field import HierarchyField, GeoCodeField, TextField, ShortCodeField
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME, LOCATION_TYPE_FIELD_CODE, GEO_CODE_FIELD_NAME, GEO_CODE, REPORTER
from mangrove.contrib.registration_validators import AtLeastOneLocationFieldMustBeAnsweredValidator, MobileNumberValidationsForReporterRegistrationValidator

class TestAtLeastOneLocationFieldMustBeAnsweredValidator(unittest.TestCase):
    def setUp(self):
        self.validator = AtLeastOneLocationFieldMustBeAnsweredValidator()
        self.field1 = HierarchyField(name=LOCATION_TYPE_FIELD_NAME, code=LOCATION_TYPE_FIELD_CODE,
            label="What is the subject's location?", instruction="Enter a region, district, or commune",
            required=False)
        self.field2 = GeoCodeField(name=GEO_CODE_FIELD_NAME, code=GEO_CODE, label="What is the subject's GPS co-ordinates?"
            , instruction="Enter lat and long. Eg 20.6, 47.3",
            required=False)
        self.field3 = TextField('a', 'a', 'a')
        self.field4 = TextField('b', 'b', 'b')

        self.fields = [self.field1, self.field2, self.field3, self.field4]

    def test_should_return_error_dict_if_mobile_number_field_missing(self):
        values = dict(a='test2', b='reporter')
        error_dict = self.validator.validate(values, self.fields)
        self.assertEqual(1, len(error_dict))
        self.assertTrue(GEO_CODE in error_dict)

    def test_should_create_mobile_number_mandatory_for_reporter_validator_from_json(self):
        validator_json = {
            'cls': ValidatorTypes.At_Least_One_Location_Field_Must_Be_Answered
        }

        self.assertTrue(isinstance(validator_factory(validator_json), AtLeastOneLocationFieldMustBeAnsweredValidator))

    def test_mobile_number_mandatory_for_reporter_validator_should_be_serializable(self):
        expected_json = {
            'cls': ValidatorTypes.At_Least_One_Location_Field_Must_Be_Answered
        }
        self.assertEqual(expected_json, self.validator.to_json())


class TestMobileNumberMandatoryValidationsForReporterRegistrationValidator(unittest.TestCase):

    def setUp(self):
        self.validator = MobileNumberValidationsForReporterRegistrationValidator()
        self.field1 = ShortCodeField('t', 't', 't')
        self.field2 = TextField('m', 'm', 'm')
        self.fields = [self.field1, self.field2]
        self.dbm = Mock(spec=DatabaseManager)
        self.dbm.view = Mock()
        self.dbm.view.datasender_by_mobile = Mock(return_value=[{'doc':{
            "data":{"mobile_number":{"value":"123"}},
            "short_code":"abc"
        }}])

    def test_should_return_error_dict_if_mobile_number_allready_exist(self):
        entity_mock = Mock()
        entity_mock.value.return_value='123'
        values = dict(t='reporter', m='123')
        error_dict = self.validator.validate(values, self.fields, self.dbm)
        self.assertEqual(1, len(error_dict))
        self.assertTrue('m' in error_dict.keys())

    def test_should_create_mobile_number_mandatory_for_reporter_validator_from_json(self):
        validator_json = {
            'cls': ValidatorTypes.MOBILE_NUMBER_MANDATORY_FOR_REPORTER
        }

        self.assertTrue(isinstance(validator_factory(validator_json), MobileNumberValidationsForReporterRegistrationValidator))

    def test_mobile_number_mandatory_for_reporter_validator_should_be_serializable(self):
        expected_json = {
            'cls': ValidatorTypes.MOBILE_NUMBER_MANDATORY_FOR_REPORTER
        }
        self.assertEqual(expected_json, self.validator.to_json())

    def test_should_return_error_if_mobile_number_comes_in_epsilon_format_from_excel_file(self):
        entity_mock = Mock()
        entity_mock.value.return_value='266123321435'
        values = dict(t='reporter', m='2.66123321435e+11')
        error_dict = self.validator.validate(values, self.fields, self.dbm)
        self.assertEqual(1, len(error_dict))
        self.assertTrue('m' in error_dict.keys())

    def test_should_return_error_if_mobile_number_has_hyphens_from_excel_file(self):
        entity_mock = Mock()
        entity_mock.value.return_value='266123321435'
        values = dict(t='reporter', m='266-123321435')
        error_dict = self.validator.validate(values, self.fields, self.dbm)
        self.assertEqual(1, len(error_dict))
        self.assertTrue('m' in error_dict.keys())

    def test_should_return_error_if_mobile_number_comes_as_floating_point_number_from_excel_file(self):
        entity_mock = Mock()
        entity_mock.value.return_value='266123321435'
        values = dict(t='reporter', m='266123321435.0')
        error_dict = self.validator.validate(values, self.fields, self.dbm)
        self.assertEqual(1, len(error_dict))
        self.assertTrue('m' in error_dict.keys())

