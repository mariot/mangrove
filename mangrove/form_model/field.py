from collections import OrderedDict
import re
import abc

from datetime import datetime
from babel.dates import format_date
from mangrove.data_cleaner import TelephoneNumber
from mangrove.errors.MangroveException import AnswerTooBigException, AnswerTooSmallException, AnswerWrongType, \
    IncorrectDate, AnswerTooLongException, AnswerTooShortException, GeoCodeFormatException, \
    RequiredFieldNotPresentException
from mangrove.form_model.validation import ChoiceConstraint, GeoCodeConstraint, constraints_factory, \
    TextLengthConstraint, ShortCodeRegexConstraint
from coverage.html import escape
from mangrove.utils.types import is_sequence, is_empty, sequence_to_str
from mangrove.validate import VdtValueTooBigError, VdtValueTooSmallError, VdtTypeError, VdtValueTooShortError, \
    VdtValueTooLongError


def create_question_from(dictionary, dbm):
    """
     Given a dictionary that defines a question, this would create a field with all the validations that are
     defined on it.
    """
    type = dictionary.get("type")
    name = dictionary.get("name")
    code = dictionary.get("code")
    label = dictionary.get("label")
    instruction = dictionary.get("instruction")
    required = dictionary.get("required")
    unique_id_type = dictionary.get("unique_id_type")
    parent_field_code = dictionary.get("parent_field_code")
    if type == field_attributes.TEXT_FIELD:
        return _get_text_field(code, dictionary, label, name, instruction, required, parent_field_code)
    elif type == field_attributes.INTEGER_FIELD:
        return _get_integer_field(code, dictionary, label, name, instruction, required, parent_field_code)
    elif type == field_attributes.DATE_FIELD:
        return _get_date_field(code, dictionary, label, name, instruction, required, parent_field_code)
    elif type == field_attributes.LOCATION_FIELD:
        return _get_geo_code_field(code, instruction, label, name, required, parent_field_code)
    elif type == field_attributes.SELECT_FIELD or type == field_attributes.MULTISELECT_FIELD:
        return _get_select_field(code, dictionary, label, name, type, instruction, required, parent_field_code)
    elif type == field_attributes.LIST_FIELD:
        return _get_list_field(name, code, label, instruction, required, parent_field_code)
    elif type == field_attributes.TELEPHONE_NUMBER_FIELD:
        return _get_telephone_number_field(code, dictionary, label, name, instruction, required, parent_field_code)
    elif type == field_attributes.SHORT_CODE_FIELD:
        return _get_short_code_field(code, dictionary, label, name, instruction, required, parent_field_code)
    elif type == field_attributes.UNIQUE_ID_FIELD:
        return _get_unique_id_field(unique_id_type, code, dictionary, label, name, instruction, required,
                                    parent_field_code)
    elif type == field_attributes.FIELD_SET:
        return _get_field_set_field(code, dictionary, label, name, instruction, required, dbm, parent_field_code)
    elif type == field_attributes.IMAGE:
        return _get_image_field(code, dictionary, label, name, instruction, required, parent_field_code)

    return None


def _get_image_field(code, dictionary, label, name, instruction, required, parent_field_code):
    constraints, constraints_json = [], dictionary.get("constraints")
    if constraints_json is not None:
        constraints = constraints_factory(constraints_json)
    field = ImageField(name=name, code=code, label=label, constraints=constraints, instruction=instruction,
                       required=required, parent_field_code=parent_field_code)
    return field


def _get_field_set_field(code, dictionary, label, name, instruction, required, dbm, parent_field_code):
    constraints, constraints_json = [], dictionary.get("constraints")
    if constraints_json is not None:
        constraints = constraints_factory(constraints_json)

    sub_fields = dictionary.get("fields")
    fieldset_type = dictionary.get("fieldset_type")
    repeat_question_fields = [create_question_from(f, dbm) for f in sub_fields]
    field = FieldSet(name=name, code=code, label=label, instruction=instruction, required=required,
                     field_set=repeat_question_fields, fieldset_type=fieldset_type, parent_field_code=parent_field_code)
    return field


def _get_text_field(code, dictionary, label, name, instruction, required, parent_field_code):
    constraints, constraints_json = [], dictionary.get("constraints")
    if constraints_json is not None:
        constraints = constraints_factory(constraints_json)
    field = TextField(name=name, code=code, label=label,
                      constraints=constraints, instruction=instruction, required=required,
                      parent_field_code=parent_field_code, is_calculated=dictionary.get('is_calculated'))
    return field


def _get_short_code_field(code, dictionary, label, name, instruction, required, parent_field_code):
    constraints, constraints_json = [], dictionary.get("constraints")
    if constraints_json is not None:
        constraints = constraints_factory(constraints_json)
    field = ShortCodeField(name=name, code=code, label=label,
                           constraints=constraints, instruction=instruction, required=required,
                           parent_field_code=parent_field_code)
    return field


def _get_unique_id_field(unique_id_type, code, dictionary, label, name, instruction, required, parent_field_code):
    return UniqueIdField(unique_id_type=unique_id_type, name=name, code=code,
                         label=dictionary.get("label"),
                         instruction=dictionary.get("instruction"), parent_field_code=parent_field_code)


def _get_telephone_number_field(code, dictionary, label, name, instruction, required, parent_field_code):
    constraints, constraints_json = [], dictionary.get("constraints")
    if constraints_json is not None:
        constraints = constraints_factory(constraints_json)

    field = TelephoneNumberField(name=name, code=code, label=label, constraints=constraints,
                                 instruction=instruction, required=required, parent_field_code=parent_field_code)

    return field


def _get_integer_field(code, dictionary, label, name, instruction, required, parent_field_code):
    constraints, constraint_list = [], dictionary.get('constraints')
    if constraint_list is not None:
        constraints = constraints_factory(constraint_list)

    integer_field = IntegerField(name=name, code=code, label=label, instruction=instruction,
                                 constraints=constraints, required=required, parent_field_code=parent_field_code)

    return integer_field


def _get_date_field(code, dictionary, label, name, instruction, required, parent_field_code):
    date_format = dictionary.get("date_format")

    date_field = DateField(name=name, code=code, label=label, date_format=date_format,
                           instruction=instruction, required=required, parent_field_code=parent_field_code)

    return date_field


def _get_select_field(code, dictionary, label, name, type, instruction, required, parent_field_code):
    choices = dictionary.get("choices")
    single_select = True if type == field_attributes.SELECT_FIELD else False

    field = SelectField(name=name, code=code, label=label, options=choices, single_select_flag=single_select,
                        instruction=instruction, required=required, parent_field_code=parent_field_code)

    return field


def _get_list_field(name, code, label, instruction, required, parent_field_code):
    field = HierarchyField(name, code, label, instruction=instruction, required=required,
                           parent_field_code=parent_field_code)

    return field


def _get_geo_code_field(code, instruction, label, name, required, parent_field_code):
    field = GeoCodeField(name=name, code=code, label=label, instruction=instruction,
                         required=required, parent_field_code=parent_field_code)

    return field


def field_to_json(object):
    # assert isinstance(object, Field)
    if isinstance(object, datetime):
        return object.isoformat()
    else:
        return object._to_json_view()


class field_attributes(object):
    """Constants for referencing standard attributes in questionnaire."""
    LANGUAGE = "language"
    FIELD_CODE = "code"
    INSTRUCTION = "instruction"
    INTEGER_FIELD = "integer"
    TEXT_FIELD = "text"
    SHORT_CODE_FIELD = "short_code"
    TELEPHONE_NUMBER_FIELD = "telephone_number"
    SELECT_FIELD = 'select1'
    LOCATION_FIELD = "geocode"
    DATE_FIELD = 'date'
    MULTISELECT_FIELD = 'select'
    DEFAULT_LANGUAGE = "en"
    ENTITY_QUESTION_FLAG = 'entity_question_flag'
    NAME = "name"
    LIST_FIELD = "list"
    UNIQUE_ID_FIELD = "unique_id"
    FIELD_SET = "field_set"
    IMAGE = "image"


class Field(object):
    def __init__(self, type="", name="", code="", label='', instruction='',
                 constraints=None, required=True, parent_field_code=None):
        if not constraints: constraints = []
        self._dict = {}
        self._dict = {'name': name, 'type': type, 'code': code, 'instruction': instruction,
                      'label': label, 'required': required, 'parent_field_code': parent_field_code}
        self.constraints = constraints
        self.errors = []
        self.value = None
        if not is_empty(constraints):
            self._dict['constraints'] = []
            for constraint in constraints:
                constraint_json = constraint._to_json()
                if not is_empty(constraint_json):
                    self._dict['constraints'].append(constraint_json)

    @property
    def name(self):
        return self._dict.get("name")

    def set_name(self, new_name):
        self._dict["name"] = new_name

    def set_label(self, new_label):
        self._dict["label"] = new_label

    def set_instruction(self, new_instruction):
        self._dict["instruction"] = new_instruction

    def set_constraints(self, new_constraints):
        self._dict["constraints"] = new_constraints
        self.constraints = new_constraints

    @property
    def label(self):
        return self._dict.get('label')

    @property
    def type(self):
        return self._dict.get('type')

    @property
    def code(self):
        return self._dict.get('code')

    @property
    def instruction(self):
        return self._dict.get('instruction')


    @property
    def parent_field_code(self):
        return self._dict.get('parent_field_code')

    @property
    def is_entity_field(self):
        return False

    @property
    def is_event_time_field(self):
        return False

    @property
    def is_field_set(self):
        return False

    def _to_json(self):
        dict = self._dict.copy()
        dict['instruction'] = self._dict['instruction']

        return dict

    def _to_json_view(self):
        json = self._to_json()

        if 'constraints' in json:
            constraints = json.pop('constraints')
            for constraint in constraints:
                json[constraint[0]] = constraint[1]
        return json

    def set_value(self, value):
        self.value = value

    def get_constraint_text(self):
        return ""

    def is_required(self):
        return self._dict['required']

    def set_required(self, required):
        self._dict["required"] = required

    def validate(self, value):
        if self.is_required() and is_empty(value):
            raise RequiredFieldNotPresentException(self.code)

    def convert_to_unicode(self):
        if self.value is None:
            return unicode("")
        return unicode(self.value)

    def stringify(self):
        return self.convert_to_unicode()

    def xform_constraints(self):
        return " and ".join(filter(None, [constraint.xform_constraint() for constraint in self.constraints]))

    @abc.abstractmethod
    def formatted_field_values_for_excel(self, value):
        pass


class IntegerField(Field):
    def __init__(self, name, code, label, instruction=None,
                 constraints=None, required=True, parent_field_code=None):
        if not constraints: constraints = []
        Field.__init__(self, type=field_attributes.INTEGER_FIELD, name=name, code=code,
                       label=label, instruction=instruction, constraints=constraints, required=required,
                       parent_field_code=parent_field_code)

    def validate(self, value):
        Field.validate(self, value)
        try:
            for constraint in self.constraints:
                constraint.validate(value)
            try:
                return int(value)
            except Exception:
                return float(value)
        except VdtValueTooBigError:
            raise AnswerTooBigException(self._dict[field_attributes.FIELD_CODE], value)
        except VdtValueTooSmallError:
            raise AnswerTooSmallException(self._dict[field_attributes.FIELD_CODE], value)
        except VdtTypeError:
            raise AnswerWrongType(self._dict[field_attributes.FIELD_CODE], value)

    def get_constraint_text(self):
        max, min = self._get_max_min()
        if min is not None and max is None:
            constraint_text = "Minimum %s" % min
            return constraint_text
        if min is None and max is not None:
            constraint_text = "Upto %s" % max
            return constraint_text
        elif min is not None and max is not None:
            constraint_text = "%s -- %s" % (min, max)
            return constraint_text
        return ""

    def _get_max_min(self):
        max = min = None
        if len(self.constraints) > 0:
            constraint = self.constraints[0]
            min = constraint.min
            max = constraint.max
        return max, min

    def formatted_field_values_for_excel(self, value):
        try:
            if value is None:
                return ""
            return float(value)
        except ValueError:
            return value


class DateField(Field):
    DATE_FORMAT = "date_format"
    DATE_DICTIONARY = {'mm.yyyy': '%m.%Y', 'dd.mm.yyyy': '%d.%m.%Y', 'mm.dd.yyyy': '%m.%d.%Y', 'yyyy': '%Y'}
    FORMAT_DATE_DICTIONARY = {'mm.yyyy': 'MM.yyyy', 'dd.mm.yyyy': 'dd.MM.yyyy', 'mm.dd.yyyy': 'MM.dd.yyyy',
                              'submission_date_format': 'MMM. dd, yyyy, hh:mm a', 'yyyy': 'yyyy'}

    def __init__(self, name, code, label, date_format, instruction=None,
                 required=True, parent_field_code=None):
        Field.__init__(self, type=field_attributes.DATE_FIELD, name=name, code=code,
                       label=label, instruction=instruction, required=required, parent_field_code=parent_field_code)
        self._dict[self.DATE_FORMAT] = date_format

    def validate(self, value):
        Field.validate(self, value)
        return self.__date__(value)

    @property
    def date_format(self):
        return self._dict.get(self.DATE_FORMAT)

    @property
    def is_monthly_format(self):
        return self.date_format == 'mm.yyyy'

    def get_constraint_text(self):
        return self.date_format

    def convert_to_unicode(self):
        if self.value is None:
            return unicode("")
        date_format = self.FORMAT_DATE_DICTIONARY.get(self.date_format)
        return format_date(self.value, date_format) if isinstance(self.value, datetime) else unicode(self.value)

    def formatted_field_values_for_excel(self, value):
        try:
            if value is None:
                return ""
            return ExcelDate(self.__date__(value), self.date_format)
        except IncorrectDate:
            return value

    def __date__(self, date_string):
        try:
            return datetime.strptime(date_string.strip(), DateField.DATE_DICTIONARY.get(self.date_format))
        except ValueError:
            raise IncorrectDate(self._dict.get(field_attributes.FIELD_CODE), date_string,
                                self._dict.get(self.DATE_FORMAT))


# All the Field Types should be be wrapped with Excel Field types defined in other project including the lead part fields.
#That will require atleast a couple of days of work
class ExcelDate(object):
    DATE_DICTIONARY = {'mm.yyyy': '%m.%Y', 'dd.mm.yyyy': '%d.%m.%Y', 'mm.dd.yyyy': '%m.%d.%Y'}

    def __init__(self, date, date_format):
        self.date = date
        self.date_format = date_format

    def date_as_string(self):
        '''This is implemented for KeywordFilter.filter method. Ideally we should pass in the keyword here and return true or false.'''
        return self.date.strftime(ExcelDate.DATE_DICTIONARY.get(self.date_format, '%b. %d, %Y, %I:%M %p'))

    def __eq__(self, other):
        return self.date == other.date


class TextField(Field):
    DEFAULT_VALUE = "defaultValue"
    CONSTRAINTS = "constraints"

    def __init__(self, name, code, label, constraints=None, defaultValue="", instruction=None,
                 required=True, parent_field_code=None, is_calculated=False):
        if not constraints: constraints = []
        assert isinstance(constraints, list)
        Field.__init__(self, type=field_attributes.TEXT_FIELD, name=name, code=code,
                       label=label, instruction=instruction, constraints=constraints, required=required,
                       parent_field_code=parent_field_code)
        self.value = self._dict[self.DEFAULT_VALUE] = defaultValue if defaultValue is not None else ""
        if is_calculated:
            self.is_calculated = True


    @property
    def is_calculated(self):
        return self._dict.get("is_calculated", False)

    @is_calculated.setter
    def is_calculated(self, is_calculated):
        self._dict["is_calculated"] = is_calculated

    def set_value(self, value):
        self.value = "" if self.is_calculated and value in ['NaN', 'Invalid Date'] else value

    def validate(self, value):
        Field.validate(self, value)
        try:
            value = value.strip()
            for constraint in self.constraints:
                value = constraint.validate(value)
            return value
        except VdtValueTooLongError as valueTooLongError:
            raise AnswerTooLongException(self._dict[field_attributes.FIELD_CODE], value, valueTooLongError.args[1])
        except VdtValueTooShortError as valueTooShortError:
            raise AnswerTooShortException(self._dict[field_attributes.FIELD_CODE], value, valueTooShortError.args[1])


    def get_constraint_text(self):
        if not is_empty(self.constraints):
            length_constraint = self.constraints[0]
            min = length_constraint.min
            max = length_constraint.max
            if min is not None and max is None:
                constraint_text = "Minimum %s characters" % min
                return constraint_text
            if min is None and max is not None:
                constraint_text = "Upto %s characters" % max
                return constraint_text
            elif min is not None and max is not None:
                constraint_text = "Between %s -- %s characters" % (min, max)
                return constraint_text
        return ""

    def formatted_field_values_for_excel(self, value):
        return value


class UniqueIdField(Field):
    def __init__(self, unique_id_type, name, code, label, constraints=None, defaultValue=None, instruction=None,
                 required=True, parent_field_code=None):
        if not constraints: constraints = []
        assert isinstance(constraints, list)
        Field.__init__(self, type=field_attributes.UNIQUE_ID_FIELD, name=name, code=code, label=label,
                       instruction=instruction,
                       constraints=constraints, required=required, parent_field_code=parent_field_code)
        self.unique_id_type = unique_id_type

    def validate(self, value):
        super(UniqueIdField, self).validate(value)
        return value.lower()

    @property  #TODO:Remove
    def is_entity_field(self):
        return True

    def _to_json(self):
        dict = super(UniqueIdField, self)._to_json()
        dict['unique_id_type'] = self.unique_id_type
        return dict

    def stringify(self):
        return unicode("%s(%s)" % (unicode(self.unique_id_type.capitalize()), self.convert_to_unicode() ))

    def set_value(self, value):
        if value:
            self.value = value.lower()


class TelephoneNumberField(TextField):
    def __init__(self, name, code, label, constraints=None, defaultValue=None, instruction=None,
                 required=True, parent_field_code=None):
        if not constraints: constraints = []
        assert isinstance(constraints, list)
        TextField.__init__(self, name=name, code=code, label=label, instruction=instruction, constraints=constraints,
                           defaultValue=defaultValue,
                           required=required, parent_field_code=parent_field_code)
        self._dict['type'] = field_attributes.TELEPHONE_NUMBER_FIELD

    def _clean(self, value):
        return TelephoneNumber().clean(value)

    def validate(self, value):
        value = self._clean(value)
        return super(TelephoneNumberField, self).validate(value)


class ShortCodeField(TextField):
    def __init__(self, name, code, label, constraints=None, defaultValue=None, instruction=None,
                 required=False, parent_field_code=None):
        if not constraints:
            constraints = [TextLengthConstraint(max=20), ShortCodeRegexConstraint("^[a-zA-Z0-9]+$")]
        assert isinstance(constraints, list)
        TextField.__init__(self, name=name, code=code, label=label, instruction=instruction, constraints=constraints,
                           defaultValue=defaultValue,
                           required=required, parent_field_code=parent_field_code)
        self._dict['type'] = field_attributes.SHORT_CODE_FIELD


    def _clean(self, value):
        return value.lower() if value else None

    def validate(self, value):
        value = self._clean(value)
        return super(ShortCodeField, self).validate(value)

    @property  #TODO:Remove
    def is_entity_field(self):
        return True


class HierarchyField(Field):
    def __init__(self, name, code, label, instruction=None,
                 required=True, parent_field_code=None):
        Field.__init__(self, type=field_attributes.LIST_FIELD, name=name, code=code,
                       label=label, instruction=instruction, required=required, parent_field_code=parent_field_code)

    def validate(self, value):
        Field.validate(self, value)
        if is_sequence(value) or value is None:
            return value
        return [value]

    def convert_to_unicode(self):
        if self.value is None:
            return unicode("")
        return sequence_to_str(self.value) if isinstance(self.value, list) else unicode(self.value)


class SelectField(Field):
    '''option values for this should contain single letters like a,b,c,d etc and after 26 options should start with a number followed by single character
    like 1a,1b,1c,1d etc '''
    OPTIONS = "choices"

    def __init__(self, name, code, label, options, instruction=None,

                 single_select_flag=True, required=True, parent_field_code=None):
        assert len(options) > 0
        type = field_attributes.SELECT_FIELD if single_select_flag else field_attributes.MULTISELECT_FIELD
        self.single_select_flag = single_select_flag
        Field.__init__(self, type=type, name=name, code=code,
                       label=label, instruction=instruction, required=required, parent_field_code=parent_field_code)
        self._dict[self.OPTIONS] = []
        valid_choices = self._dict[self.OPTIONS]
        if options is not None:
            for option in options:
                if isinstance(option, tuple):
                    single_language_specific_option = {'text': option[0], 'val': option[1]}
                elif isinstance(option, dict):
                    single_language_specific_option = option
                else:
                    single_language_specific_option = {'text': option, 'val': option}
                valid_choices.append(single_language_specific_option)
        self.constraint = ChoiceConstraint(
            list_of_valid_choices=valid_choices,
            single_select_constraint=single_select_flag, code=code)

    SINGLE_SELECT_FLAG = 'single_select_flag'

    def validate(self, value):
        Field.validate(self, value)
        return self.constraint.validate(answer=value)

    @property
    def options(self):
        return self._dict.get(self.OPTIONS)

    def _to_json_view(self):
        dict = self._dict.copy()
        return dict

    def get_constraint_text(self):
        return [option["text"] for option in self.options]

    def convert_to_unicode(self):
        if self.value is None:
            return unicode("")
        return unicode(",".join([unicode(i) for i in self.value])) if isinstance(self.value, list) else unicode(
            self.value)

    # def _get_value_by_option(self, option):
    #     for opt in self.options:
    #         opt_text = opt['text']
    #         opt_value = opt['val']
    #         if opt_value.lower() == option.lower():
    #             return opt_text
    #     return None

    @property
    def is_single_select(self):
        return self.type == "select1"

    def get_value_by_option(self, option):
        for opt in self.options:
            opt_text = opt['text']
            opt_value = opt['val']
            if opt_value.lower() == option.lower():
                return opt_text
        return None


    def get_option_value_list(self, question_value):
        options = self.get_option_list(question_value)
        result = []
        for option in options:
            option_value = self.get_value_by_option(option)
            if option_value:
                result.append(option_value)
        return result

    def get_option_list(self, question_value):
        if question_value is None: return []

        question_value = question_value.lower()

        if ',' in question_value:
            responses = question_value.split(',')
            responses = [r.strip() for r in responses]
        elif ' ' in question_value:
            responses = question_value.split(' ')
        elif question_value in [item.get('val') for item in self._dict[self.OPTIONS]]:
            # yes in ['yes','no']
            responses = [question_value]
        else:
            responses = re.findall(r'[1-9]?[a-zA-Z]', question_value)

        return responses


    def formatted_field_values_for_excel(self, value):
        if value is None: return []

        options = self.get_option_list(value)
        result = []
        for option in options:
            option_value = self.get_value_by_option(option)
            if option_value:
                result.append(option_value)
        return result

    def get_options_map(self):
        options_map = {}
        for option in self.options:
            options_map.update({option['val']: option['text']})
        return options_map

    def escape_option_text(self):
        for option in self._dict.get(self.OPTIONS):
            option['text'] = escape(option['text'])


class GeoCodeField(Field):
    type = field_attributes.LOCATION_FIELD

    def __init__(self, name, code, label, instruction=None, required=True, parent_field_code=None):
        Field.__init__(self, type=field_attributes.LOCATION_FIELD, name=name, code=code,
                       label=label, instruction=instruction, required=required, parent_field_code=parent_field_code)

    def validate(self, lat_long_string):
        Field.validate(self, lat_long_string)
        lat_long = lat_long_string.replace(",", " ")
        lat_long = re.sub(' +', ' ', lat_long).split(" ")
        if len(lat_long) != 2:
            raise GeoCodeFormatException(self.code)
        return GeoCodeConstraint().validate(latitude=lat_long[0], longitude=lat_long[1])

    def get_constraint_text(self):
        return "xx.xxxx yy.yyyy"

    def convert_to_unicode(self):
        if self.value is None:
            return unicode("")
        return ", ".join(str(b) for b in list(self.value)) if isinstance(self.value, list) or isinstance(self.value,
                                                                                                         tuple) else unicode(
            self.value)

    def formatted_field_values_for_excel(self, value):
        value_list = value.split(',')
        return self._empty_if_no_data(value_list, 0), self._empty_if_no_data(value_list, 1)

    def _empty_if_no_data(self, list, index):
        if len(list) < index + 1:
            return ''
        else:
            try:
                return float(list[index])
            except ValueError:
                return list[index]


class ImageField(Field):
    def formatted_field_values_for_excel(self, value):
        return value

    def __init__(self, name, code, label, constraints=None, instruction=None,
                 entity_question_flag=False, required=True, parent_field_code=None):
        if not constraints: constraints = []
        assert isinstance(constraints, list)
        Field.__init__(self, type=field_attributes.IMAGE, name=name, code=code,
                       label=label, instruction=instruction, constraints=constraints, required=required,
                       parent_field_code=parent_field_code)
        if entity_question_flag:
            self._dict[self.ENTITY_QUESTION_FLAG] = entity_question_flag


class FieldSet(Field):
    FIELDSET_TYPE = 'fieldset_type'

    def __init__(self, name, code, label, instruction=None, required=True, field_set=[], fieldset_type='group',
                 parent_field_code=None):
        Field.__init__(self, type=field_attributes.FIELD_SET, name=name, code=code,
                       label=label, instruction=instruction, required=required, parent_field_code=parent_field_code)
        self.fields = self._dict['fields'] = field_set
        self._dict[self.FIELDSET_TYPE] = fieldset_type

    @property
    def is_field_set(self):
        return True

    def is_group(self):
        return self._dict.get(self.FIELDSET_TYPE) == 'group'


    def _find_field_for_code(self, code):
        for field in self.fields:
            if field.code.lower() == code.lower():
                return field
        return None

    def set_value(self, value):
        list = []
        if value:
            for current_value in value:
                dict = OrderedDict()
                for field_code, answer in current_value.iteritems():
                    field = self._find_field_for_code(field_code)
                    if field:
                        field.set_value(answer)
                        dict.update({field_code: field.value})
                list.append(dict)
        super(FieldSet, self).set_value(list)


    @property
    def fieldset_type(self):
        return self._dict.get(self.FIELDSET_TYPE)

    def validate(self, value):
        # todo call all validators of the child fields
        Field.validate(self, value)
        if is_sequence(value) or value is None:
            return value
        return [value]

    #todo find the application of this
    def convert_to_unicode(self):
        if self.value is None:
            return unicode("")
        return sequence_to_str(self.value) if isinstance(self.value, list) else unicode(self.value)

    def _to_json(self):
        dict = self._dict.copy()
        dict['instruction'] = self._dict['instruction']
        dict['fields'] = [f._to_json() for f in self.fields]
        return dict
