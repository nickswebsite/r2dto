from .base import ValidationError, InvalidTypeValidationError, BaseField

__all__ = ("Field", "StringField", "BooleanField", "IntegerField", "FloatField", "ObjectField", "ListField")

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
        for item_i, item in enumerate(data):
            for allowed_type in self.allowed_types:
                try:
                    obj = allowed_type.clean(item)
                except ValidationError:
                    pass
                else:
                    res.append(obj)
                    break
            else:
                raise InvalidTypeValidationError("{}[{}]".format(self.name, item_i), str(self.allowed_types), type(item))

        return res
