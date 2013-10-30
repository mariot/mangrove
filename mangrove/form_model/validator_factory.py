# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.contrib.delete_validators import EntityShouldExistValidator
from mangrove.form_model.validator_types import ValidatorTypes
from mangrove.form_model.validators import MandatoryValidator, MobileNumberValidationsForReporterRegistrationValidator, AtLeastOneLocationFieldMustBeAnsweredValidator


def validator_factory(validator_json):
    validator_class = validators.get(validator_json['cls'])
    return validator_class()


validators = {
    ValidatorTypes.MANDATORY : MandatoryValidator,
    ValidatorTypes.MOBILE_NUMBER_MANDATORY_FOR_REPORTER : MobileNumberValidationsForReporterRegistrationValidator, #no-op
    ValidatorTypes.At_Least_One_Location_Field_Must_Be_Answered : AtLeastOneLocationFieldMustBeAnsweredValidator,  #no-op
    ValidatorTypes.ENTITY_SHOULD_EXIST : EntityShouldExistValidator,
    }