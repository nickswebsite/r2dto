import datetime
import re
import uuid

from .base import ValidationError, InvalidTypeValidationError, BaseField

__all__ = ("Field", "StringField", "BooleanField", "IntegerField", "FloatField",
           "ObjectField", "ListField", "DateTimeField", "InternetDateTimeField", "DateField", "TimeField", "UuidField")

TIME_TOKEN_STRIPPER_PATTERN = re.compile(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))")

Field = BaseField


class BaseTypeValidatorField(object):
    basetypes = ()

    def clean(self, data):
        if not isinstance(data, self.basetypes):
            raise InvalidTypeValidationError(self.name, str(self.basetypes), type(data))
        return data

    def object_to_data(self, obj):
        if not isinstance(obj, self.basetypes):
            raise InvalidTypeValidationError(self.object_field_name, str(self.basetypes), type(obj))
        return obj


class StringField(BaseTypeValidatorField, BaseField):
    """
    Represents a string field.
    """
    try:
        basetypes = (basestring,)
    except NameError:
        basetypes = (str,)


class BooleanField(BaseTypeValidatorField, BaseField):
    """
    Represents a boolean field.
    """
    basetypes = (bool,)


class IntegerField(BaseTypeValidatorField, BaseField):
    """
    Represents an integer field.  In python 2.7, this could be either an int or a long.  In python 3, it is just simply
    an 'int'.
    """
    basetypes = (int,)

    try:
        basetypes += (long,)
    except NameError:
        pass


class FloatField(BaseTypeValidatorField, BaseField):
    """
    Represents a floating point field.
    """
    basetypes = (float,)


class ObjectField(BaseField):
    """
    Represents an more complex object field.

    Specify the serializer to user as the argument to serialzer_class.
    """
    def __init__(self, serializer_class, *args, **kwargs):
        super(ObjectField, self).__init__(*args, **kwargs)
        self.serializer_class = serializer_class

    def clean(self, data):
        s = self.serializer_class(data=data)
        s.validate()
        return s.object

    def object_to_data(self, obj):
        s = self.serializer_class(object=obj)
        s.validate()
        return s.data


class ListField(BaseField):
    """
    Represents a list of objects of varying types.

    :param allowed_types: is either a list or tuple of Field types that are allowed in the list.  If just a field is
                          provided, then it is the only type allowed.
    """
    def __init__(self, allowed_types, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        if isinstance(allowed_types, BaseField):
            allowed_types = (allowed_types,)
        self.allowed_types = tuple(allowed_types)

    def clean(self, data):
        if not isinstance(data, list):
            raise InvalidTypeValidationError(self.name, "list", type(data))

        res = []
        errors = []
        for item_i, item in enumerate(data):
            item_errors = list()
            for allowed_type in self.allowed_types:
                try:
                    obj = allowed_type.clean(item)
                except ValidationError as ex:
                    item_errors.append('{}[{}]: {}'.format(self.name, item_i, ex))
                else:
                    res.append(obj)
                    item_errors = list()
                    break
            errors.extend(item_errors)
        if errors:
            raise ValidationError(errors)
        return res

    def object_to_data(self, obj):
        res = []
        errors = []
        for item_i, item in enumerate(obj):
            item_errors = list()
            for allowed_type in self.allowed_types:
                try:
                    data = allowed_type.object_to_data(item)
                except ValidationError as ex:
                    item_errors.append('{}[{}]: {}'.format(self.name, item_i, ex))
                else:
                    res.append(data)
                    item_errors = list()
                    break
            errors.extend(item_errors)
        if errors:
            raise ValidationError(errors)
        return res


def _default_parse_internet_datetime_string_function(s):
    stripped = re.sub(TIME_TOKEN_STRIPPER_PATTERN, "", s)
    fmt = "%Y%m%dT%H%M%S"
    if "." in stripped:
        fmt += ".%f"
    offset = datetime.timedelta(hours=0, minutes=0)
    if "-" in stripped:
        stripped, offset_str = stripped.split("-")
        offset = -datetime.timedelta(hours=int(offset_str[:2]), minutes=int(offset_str[2:4]))
    elif "+" in stripped:
        stripped, offset_str = stripped.split("+")
        offset = datetime.timedelta(hours=int(offset_str[:2]), minutes=int(offset_str[2:4]))
    elif stripped[-1] == "Z":
        stripped = stripped[:-1]
    return datetime.datetime.strptime(stripped, fmt) - offset


class DateTimeField(StringField):
    """
    Represents a datetime object.

    Pass in a format string as the fmt parameter to set the format string, or you can pass in a callable using the
    'parse' keyword.
    """
    default_fmt = "%Y-%m-%d %H:%M:%S.%f"
    instance_type = datetime.datetime

    def __init__(self, fmt=None, parse=None, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)
        self.fmt = fmt or self.default_fmt
        self.parse = parse or (lambda s: datetime.datetime.strptime(s, self.fmt))

    def clean(self, data):
        data = super(DateTimeField, self).clean(data)

        try:
            res = self.parse(data)
        except ValueError as ex:
            raise ValidationError(str(ex))
        else:
            return res

    def object_to_data(self, obj):
        if not isinstance(obj, self.instance_type):
            raise InvalidTypeValidationError(self.name, "datetime", type(obj))
        return obj.strftime(self.fmt)


class InternetDateTimeField(DateTimeField):
    """
    Represents a datetime object.  Serializes to an RFC-3339 datetime field.  Naive dates are considered to be UTC.
    """
    def __init__(self, *args, **kwargs):
        super(InternetDateTimeField, self).__init__(parse=_default_parse_internet_datetime_string_function,
                                                    *args, **kwargs)

    def object_to_data(self, obj):
        if not isinstance(obj, self.instance_type):
            raise InvalidTypeValidationError(self.name, "datetime", type(obj))
        if obj.tzinfo:
            return obj.isoformat()
        else:
            return obj.isoformat() + "Z"


class DateField(DateTimeField):
    """
    Represents a date object.
    """

    default_fmt = "%Y-%m-%d"
    instance_type = datetime.date

    def clean(self, data):
        return super(DateField, self).clean(data).date()


class TimeField(DateTimeField):
    """
    Represents a time object.
    """

    default_fmt = "%H:%M:%S.%f"
    instance_type = datetime.time

    def clean(self, data):
        return super(TimeField, self).clean(data).time()


class UuidField(StringField):
    """
    Represents a UUID.
    """

    def clean(self, data):
        data = super(UuidField, self).clean(data)

        try:
            res = uuid.UUID(data)
        except ValueError as ex:
            raise ValidationError(str(ex))
        else:
            return res

    def object_to_data(self, obj):
        if not isinstance(obj, uuid.UUID):
            raise InvalidTypeValidationError(self.name, "uuid", type(obj))
        return str(obj)
