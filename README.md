R2DTo
=====

![Build Status](https://travis-ci.org/nickswebsite/r2dto.svg?branch=master)

Pronounced R-2-D-2.

Provides django like interface for transformation and validation of arbitrary
python objects into DTOs suitable for receiving from and delivering to other services.

(Note that installation requires setuptools.)

Quick Start
-----------

Create your 'model' class

    >>> class Simpson(object):
    ...     def __init__(self):
    ...         self.first_name = ""
    ...         self.last_name = ""
    ...
    ...     def __str__(self):
    ...         return self.first_name + " " + self.last_name

Create your 'serializer' class:

    >>> class SimpsonSerializer(Serializer):
    ...     first_name = fields.StringField(name="firstName")
    ...     last_name = fields.StringField(name="lastName")
    ...
    ...     class Meta:
    ...         model = Simpson

When you get a payload that requires one of these serializers, instantiate a serializer using the `data` keyword
argument and pass in the data dictionary.

    >>> data = {
    ...     "firstName": "Homer",
    ...     "lastName": "Simpson",
    ... }
    >>> s = SimpsonSerializer(data=data)
    >>> s.validate()
    >>> str(s.object)
    'Homer Simpson'
    >>> type(s.object)
    <class '__main__.Simpson'>

To go the other way.  Pass the object you want to transfer into the constructor using the `object` keyword argument:

    >>> homer = Simpson()
    >>> homer.first_name = "Homer"
    >>> homer.last_name = "Simpson"
    >>> s = SimpsonSerializer(object=homer)
    >>> s.validate()
    >>> s.data["firstName"]
    'Homer'
    >>> s.data["lastName"]
    'Simpson'

Fields
------

To implement your own fields, derive from 'Field' and implement 'clean' and 'object_to_data'.  ValidationError should be
raise if the data is bad.

    >>> import uuid
    >>> class UUIDField(fields.Field):
    ...     def clean(self, data):
    ...         try:
    ...             return uuid.UUID(data)
    ...         except ValueError:
    ...             raise ValidationError("{} is required to conform to the canonical UUID.".format(self.name))
    ...
    ...     def object_to_data(self, obj):
    ...         return str(obj)

When you go to create your serializer, just use the field as you would any other field.

    >>> class BartSerializer(Serializer):
    ...     uuid = UUIDField()

    >>> s = BartSerializer(data={"uuid": "46b4e146-21a7-435e-a0d3-f7d6ce773085"})
    >>> s.validate()
    >>> s.object.uuid
    UUID('46b4e146-21a7-435e-a0d3-f7d6ce773085')

## Validators

You can specify custom validators for individual fields.  These are just objects with a 'validate' method that accepts
the field and the data as parameters.  ValidationError should be raised if there is a problem with validation.

    >>> class EnumValidator(object):
    ...     def __init__(self, *choices):
    ...         self.choices = choices
    ...
    ...     def validate(self, field, data):
    ...         if data not in self.choices:
    ...             raise ValidationError("{} must be one of {}.  Got {}.".format(field.name, self.choices, data))

Use the 'validators' key word argument to use the validator with a particular field.

    >>> class LisaSerializer(Serializer):
    ...     grade = fields.StringField(validators=[EnumValidator("A+", "A")])

    >>> s = LisaSerializer(data={"grade": "A+"})
    >>> s.validate()
    >>> s.object.grade
    'A+'

    >>> s = LisaSerializer(data={"grade": "A-"})
    >>> try:
    ...     s.validate()
    ... except ValidationError as ex:
    ...     print("Validation Failed")
    ...     print(ex.errors)
    Validation Failed
    ["grade must be one of ('A+', 'A').  Got A-."]

# Fields

## DateTimeField

Represents a datetime object.

Pass in a format string as the fmt parameter to set the format string, or you can pass in a callable using the
'parse' keyword.

    >>> import datetime

    >>> class MaggieSerializer(Serializer):
    ...     birthday = fields.DateTimeField()

    >>> s = MaggieSerializer(data={"birthday": "1989-12-05 20:00:00.000000"})
    >>> s.validate()
    >>> s.object.birthday
    datetime.datetime(1989, 12, 5, 20, 0)

You can also pass in a 'parse' function into the field constructor:

    >>> def my_parse_date(datestr):
    ...     return datetime.datetime.strptime(datestr, "%Y-%m-%d %H-%M-%S")

    >>> class MargeSerializer(Serializer):
    ...     anniversary = fields.DateTimeField(parse=my_parse_date)

    >>> s = MargeSerializer(data={"anniversary": "1979-02-23 05-02-12"})
    >>> s.validate()
    >>> s.object.anniversary
    datetime.datetime(1979, 2, 23, 5, 2, 12)
