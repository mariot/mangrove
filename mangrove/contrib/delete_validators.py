from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.datastore.entity import get_by_short_code
from mangrove.form_model.field import HierarchyField, TextField, UniqueIdField, ShortCodeField
from mangrove.form_model.validator_types import ValidatorTypes
from collections import OrderedDict


class EntityShouldExistValidator(object):
    def validate(self, values, fields, dbm):
        errors = OrderedDict()
        entity_type_field, entity_id_field = self._get_field_codes(fields)
        try:
            get_by_short_code(dbm, entity_id_field.value, [entity_type_field.value])
        except DataObjectNotFound as exception:
            errors[entity_type_field.code] = exception.message
            errors[entity_id_field.code] = exception.message
        return errors

    def to_json(self):
        return dict(cls=ValidatorTypes.ENTITY_SHOULD_EXIST)

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return True
        return False

    def _get_field_codes(self, fields):
        entity_type_field, entity_id_field = None, None
        for field in fields:
            if isinstance(field, HierarchyField):
                entity_type_field = field
            if isinstance(field, UniqueIdField) or isinstance(field, ShortCodeField):
                entity_id_field = field
        return entity_type_field, entity_id_field


