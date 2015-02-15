# Copied from the 'six' module.
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


try:
    basestring
except NameError:
    basestring = str


class ValidationError(Exception):
    def __init__(self, errors):
        if isinstance(errors, basestring):
            errors = [errors]
        self.errors = errors
        super(ValidationError, self).__init__(str(self.errors))


class InvalidTypeValidationError(ValidationError):
    def __init__(self, field_name, expected, got):
        super(InvalidTypeValidationError, self).__init__("{} must be a {}.  Got {}.".format(field_name, expected, got))


class BaseField(object):
    def __init__(self, name=None, required=False, allow_null=True, validators=None):
        self.name = name
        self.object_field_name = name
        self.required = required
        self.allow_null = allow_null
        self.parent = None
        self.validators = validators or []

    def clean(self, data):
        return data

    def base_clean(self, data):
        if data is None:
            if not self.allow_null:
                raise ValidationError("{}/{} cannot be null/None".format(self.name, self.object_field_name))
            return None
        data = self.clean(data)
        for validator in self.validators:
            validator.validate(self, data)
        return data

    def object_to_data(self, obj):
        return obj

    def base_object_to_data(self, obj):
        if obj is None:
            if not self.allow_null:
                raise ValidationError("{}/{} cannot be null/None".format(self.name, self.object_field_name))
            return None
        return self.object_to_data(obj)


class DefaultMeta(object):
    pass


class DefaultModel(object):
    pass


class SerializerMetaclass(type):
    def __new__(cls, name, bases, attrs):
        options = DefaultMeta

        if "Meta" in attrs:
            options = attrs.pop("Meta")

        fields = []
        for k, v in attrs.items():
            if isinstance(v, BaseField):
                if v.name is None:
                    v.name = k
                v.object_field_name = k
                fields.append(v)

        new_class_attrs = {k: v for k, v in attrs.items() if not isinstance(v, BaseField)}
        new_class_attrs["fields"] = fields
        new_class_attrs["options"] = options
        ret = super(SerializerMetaclass, cls).__new__(cls, name, bases, new_class_attrs)
        for field in fields:
            field.parent = ret
        return ret


class BaseSerializer(object):
    fields = []
    options = None

    def __init__(self, data=None, object=None):
        if data is None and object is None or data is not None and object is not None:
            raise ValueError("Either 'object' or 'data' must be supplied as arguments, but not both.")
        self.data = data
        self.object = object

    def validate(self):
        self.base_validate()

    def base_validate(self):
        if self.object is None and self.data is not None:
            self.data_to_object()
        else:
            self.object_to_data()

    def data_to_object(self):
        model_class = getattr(self.options, "model", DefaultModel)
        model_class_args = getattr(self.options, "model_init_args", ())
        model_class_kwargs = getattr(self.options, "model_init_kwargs", {})

        errors = []
        for field in self.fields:
            if field.required and field.name not in self.data:
                errors.append("Field {} is missing.".format(field.name))

        if errors:
            raise ValidationError(errors)

        obj = model_class(*model_class_args, **model_class_kwargs)
        for field in self.fields:
            try:
                field_obj = field.base_clean(self.data[field.name])
            except ValidationError as ex:
                errors.extend(ex.errors)
            except KeyError:
                pass
            else:
                setattr(obj, field.object_field_name, field_obj)

        if errors:
            raise ValidationError(errors)

        self.object = obj

    def object_to_data(self):
        errors = []
        for field in self.fields:
            if field.required and not hasattr(self.object, field.object_field_name):
                errors.append("Field {} is missing from object.".format(field.object_field_name))

        if errors:
            raise ValidationError(errors)

        data = {}
        for field in self.fields:
            try:
                field_data = field.base_object_to_data(getattr(self.object, field.object_field_name))
            except ValidationError as ex:
                errors.extend(ex.errors)
            else:
                data[field.name] = field_data

        if errors:
            raise ValidationError(errors)

        self.data = data


class Serializer(with_metaclass(SerializerMetaclass, BaseSerializer)):
    """
    Base class for a new serializer.
    """
    pass
