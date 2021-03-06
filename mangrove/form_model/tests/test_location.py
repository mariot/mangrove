import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import HierarchyField, GeoCodeField
from mangrove.form_model.form_model import FormModel, LOCATION_TYPE_FIELD_NAME, LOCATION_TYPE_FIELD_CODE, GEO_CODE_FIELD_NAME, GEO_CODE
from mangrove.form_model.location import Location
from mangrove.utils.geo_utils import convert_to_geometry
from mangrove.utils.test_utils.dummy_location_tree import DummyLocationTree, TEST_LAT, TEST_LONG, TEST_LOCATION_HIERARCHY_FOR_GEO_CODE

class TestLocation(unittest.TestCase):
    def setUp(self):
        self.lowest_level_location = 'pune'
        self.location = Location(DummyLocationTree(), self.form())

    def test_should_not_do_anything_when_location_and_geo_is_not_present_for_submission(self):
        submission={'name':'something'}
        self.assertEquals(submission,self.location.process_submission(submission))

    def test_should_convert_location_to_location_hierarchy(self):
        submission={LOCATION_TYPE_FIELD_CODE: self.lowest_level_location,'q':"sdasd"}
        augmented_submission={LOCATION_TYPE_FIELD_CODE:['pune','mh','india'],'q':"sdasd"}
        self.assertEquals(augmented_submission,self.location.process_submission(submission))

    def test_should_convert_location_to_location_hierarchy_when_there_are_multiple_levels(self):
        submission={LOCATION_TYPE_FIELD_CODE: 'a,b','q':"sdasd"}
        augmented_submission={LOCATION_TYPE_FIELD_CODE:['a','b'],'q':"sdasd"}
        self.assertEquals(augmented_submission,self.location.process_submission(submission))

    def test_should_aggregate_highest_level_locations_when_levels_exceed_max_level_in_location_tree(self):
        submission={LOCATION_TYPE_FIELD_CODE: 'a,b,c,d,e,mada','q':"sdasd"}
        augmented_submission={LOCATION_TYPE_FIELD_CODE:['a,b','c','d','e','mada'],'q':"sdasd"}
        self.assertEquals(augmented_submission,self.location.process_submission(submission))

    def test_should_not_do_anything_when_location_and_geo_is_not_present_for_entity_creation(self):
        answers={'name':'something'}
        self.assertEquals((None,None),self.location.process_entity_creation(answers))

    def test_case_when_location_is_present_and_geo_code_is_not_present_for_entity_creation(self):
        location_hierarchy = ['pune', 'mh', 'india']
        answers={LOCATION_TYPE_FIELD_CODE: location_hierarchy,'q':"test answer"}
        self.assertEquals((location_hierarchy,convert_to_geometry((TEST_LAT,TEST_LONG))),self.location.process_entity_creation(answers))

    def test_case_when_location_is_not_found_in_location_tree(self):
        location_hierarchy = ['jalgaon', 'mh', 'india']
        answers={LOCATION_TYPE_FIELD_CODE: location_hierarchy,'q':"test answer"}
        self.assertEquals((location_hierarchy,None),self.location.process_entity_creation(answers))

    def test_case_when_location_is_not_present_and_geo_code_is_present_for_entity_creation(self):
        answers={GEO_CODE: (-12, 60),'q':"sdasd"}
        self.assertEquals((TEST_LOCATION_HIERARCHY_FOR_GEO_CODE,convert_to_geometry((TEST_LAT,TEST_LONG))),self.location.process_entity_creation(answers))

    def test_case_when_location_is_present_and_geo_code_is_present_for_entity_creation(self):
        location_hierarchy = ['pune', 'mh', 'india']
        answers={GEO_CODE: (-12, 60),LOCATION_TYPE_FIELD_CODE: location_hierarchy}
        self.assertEquals((location_hierarchy,convert_to_geometry((TEST_LAT,TEST_LONG))),self.location.process_entity_creation(answers))

    def location_hierarchy_stub(self,lowest_level_location_name):
        if lowest_level_location_name=='pune':
            return ['pune','mh','india']

    def form(self):
        manager=Mock(spec=DatabaseManager)
        question4 = HierarchyField(name=LOCATION_TYPE_FIELD_NAME, code=LOCATION_TYPE_FIELD_CODE,
            label=LOCATION_TYPE_FIELD_NAME)
        question5 = GeoCodeField(name=GEO_CODE_FIELD_NAME, code=GEO_CODE, label="What is the subject's GPS co-ordinates?")
        form_model = FormModel(manager, name="asd", form_code="asd", fields=[
            question4,question5])
        return form_model

