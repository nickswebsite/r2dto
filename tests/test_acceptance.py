# import datetime
from datetime import timedelta, datetime, date, time
import random
import unittest
import uuid

import pytz

from r2dto.fields import StringField, BooleanField, FloatField, IntegerField, ListField, ObjectField, \
    InternetDateTimeField, DateTimeField, UuidField, DateField, TimeField, \
    _default_parse_internet_datetime_string_function
from r2dto import Serializer, ValidationError


class AcceptanceTests(unittest.TestCase):
    def test_complex_types(self):
        class SubObj(object):
            def __init__(self, field="Field One"):
                self.field = field

            def __eq__(self, other):
                try:
                    return self.field == other.field
                except AttributeError:
                    return False

        class Obj(object):
            def __init__(self):
                self.list_field = []
                self.sub_obj = SubObj()

        class SubObjSerializer(Serializer):
            class Meta:
                model = SubObj

            field = StringField(required=True, allow_null=False)

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            sub_obj = ObjectField(SubObjSerializer, required=True, allow_null=False)
            list_field = ListField(StringField(), required=True, allow_null=False)

        o = Obj()
        o.sub_obj.field = "Field One"
        o.list_field = ["Hi"]

        s = ObjSerializer(object=o)
        s.validate()
        self.assertEqual(s.data["sub_obj"]["field"], o.sub_obj.field)
        self.assertEqual(o.list_field, s.data["list_field"])

        data = {
            "sub_obj": {
                "field": "Some String Field Value",
            },
            "list_field": [
                "listItemOne",
                "listItemTwo"
            ]
        }

        s2 = ObjSerializer(data=data)
        s2.validate()
        self.assertEqual(s2.object.sub_obj.field, data["sub_obj"]["field"])
        self.assertEqual(data["list_field"], s2.object.list_field)

    def test_complex_multiple_allowed_types(self):
        class SubObjOne(object):
            def __init__(self, field="Field One"):
                self.field = field

        class SubObjTwo(object):
            def __init__(self, field=0):
                self.field = field

        class Obj(object):
            def __init__(self):
                self.list_field = []
                self.sub_obj_one = SubObjOne()
                self.sub_obj_two = SubObjTwo()

        class SubObjOneSerializer(Serializer):
            class Meta:
                model = SubObjOne

            field = StringField(required=True, allow_null=False)

        class SubObjTwoSerializer(Serializer):
            class Meta:
                model = SubObjTwo

            field = IntegerField(required=True, allow_null=False)

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            sub_obj_one = ObjectField(SubObjOneSerializer, required=True, allow_null=False)
            sub_obj_two = ObjectField(SubObjTwoSerializer, required=True, allow_null=False)
            list_field = ListField(allowed_types=(StringField(), IntegerField()), required=True, allow_null=False)

        o = Obj()
        o.sub_obj_one.field = "Field One"
        o.sub_obj_two.field = 42
        o.list_field = ["Hi"]

        s = ObjSerializer(object=o)
        s.validate()
        self.assertEqual(s.data["sub_obj_one"]["field"], o.sub_obj_one.field)
        self.assertEqual(s.data["sub_obj_two"]["field"], o.sub_obj_two.field)
        self.assertEqual(o.list_field, s.data["list_field"])

        data = {
            "sub_obj_one": {
                "field": "Some String Field Value",
            },
            "sub_obj_two": {
                "field": 42,
            },
            "list_field": [
                "listItemOne",
                42
            ]
        }

        s2 = ObjSerializer(data=data)
        s2.validate()
        self.assertEqual(s2.object.sub_obj_one.field, data["sub_obj_one"]["field"])
        self.assertEqual(s2.object.sub_obj_two.field, data["sub_obj_two"]["field"])
        self.assertEqual(data["list_field"], s2.object.list_field)

    def test_list_field_with_subobjects(self):
        class SubObj(object):
            def __init__(self, field=""):
                self.field = field

        class Obj(object):
            def __init__(self):
                self.subobjs = []
                self.objfield = ""

        class SubObjSerializer(Serializer):
            class Meta:
                model = SubObj

            field = StringField()

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            objfield = StringField(name="objField", required=True, allow_null=False)
            subobjs = ListField(ObjectField(SubObjSerializer, required=True, allow_null=False),
                                name="subObjs",
                                required=True,
                                allow_null=False)

        o = Obj()
        o.objfield = "ONE"
        o.subobjs = [SubObj(field="ONE_SUB_ONE"), SubObj(field="ONE_SUB_TWO")]

        s = ObjSerializer(object=o)
        s.validate()
        self.assertEqual(o.objfield, s.data["objField"])
        self.assertEqual(o.subobjs[0].field, s.data["subObjs"][0]["field"])
        self.assertEqual(o.subobjs[1].field, s.data["subObjs"][1]["field"])

    def test_list_field_with_subobjects_of_multiple_allowed_types(self):
        class SubObjOne(object):
            def __init__(self, field=""):
                self.field = field

        class SubObjTwo(object):
            def __init__(self, field=None):
                self.field = field

        class Obj(object):
            def __init__(self):
                self.subobjs = []
                self.objfield = ""

        class SubObjOneSerializer(Serializer):
            class Meta:
                model = SubObjOne

            field = StringField()

        class SubObjTwoSerializer(Serializer):
            class Meta:
                model = SubObjTwo

            field = IntegerField()

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            objfield = StringField(name="objField", required=True, allow_null=False)
            subobjs = ListField(
                allowed_types=(
                    ObjectField(SubObjOneSerializer, required=True, allow_null=False),
                    ObjectField(SubObjTwoSerializer, required=True, allow_null=False),
                ), name="subObjs", required=True, allow_null=False)

        o = Obj()
        o.objfield = "ONE"
        o.subobjs = [SubObjOne(field="ONE_SUB_ONE"), SubObjTwo(field=42)]

        s = ObjSerializer(object=o)
        s.validate()
        self.assertEqual(o.objfield, s.data["objField"])
        self.assertEqual(o.subobjs[0].field, s.data["subObjs"][0]["field"])
        self.assertEqual(o.subobjs[1].field, s.data["subObjs"][1]["field"])

    def test_list_field_failure_with_subobjects(self):
        class SubObj(object):
            def __init__(self, field=""):
                self.field = field

        class Obj(object):
            def __init__(self, objfield="", subobjs=None):
                self.subobjs = subobjs or []
                self.objfield = objfield

        class SubObjSerializer(Serializer):
            class Meta:
                model = SubObj

            field = StringField(required=True)

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            objfield = StringField(name="objField", required=True, allow_null=False)
            subobjs = ListField(ObjectField(SubObjSerializer, required=True, allow_null=False),
                                name="subObjs", required=True, allow_null=False)

        _object = Obj("ONE", [type('FailedSubObj1', (object,), {}), SubObj(field=1), SubObj(field="ONE_SUB_TWO")])
        try:
            ObjSerializer(object=_object).validate()
            self.fail('No Exception was thrown, object should have failed validation')
        except ValidationError as ex:
            self.assertEqual("subObjs[0]: ['Field field is missing from object.']", ex.errors[0])
            self.assertEqual('subObjs[1]: ["field must be a (<class \'str\'>,).  Got <class \'int\'>."]',
                             ex.errors[1].replace('type', 'class').replace('basestring', 'str'))

        data = {'objField': 'test', 'subObjs': [{}, {'field': 1}]}
        try:
            ObjSerializer(data=data).validate()
            self.fail('No Exception was thrown, object should have failed validation')
        except ValidationError as ex:
            self.assertEqual("subObjs[0]: ['Field field is missing.']", ex.errors[0])
            self.assertEqual('subObjs[1]: ["field must be a (<class \'str\'>,).  Got <class \'int\'>."]',
                             ex.errors[1].replace('type', 'class').replace('basestring', 'str'))

    def test_list_failure(self):
        class ObjSerializer(Serializer):
            list_field = ListField(StringField(), required=True, allow_null=False)

        data = {
            "list_field": [
                "Hi",
                23
            ]
        }
        s = ObjSerializer(data=data)
        self.assertRaises(ValidationError, s.validate)

    def test_object_failure(self):
        class SubSerializer(Serializer):
            field = StringField()

        class ObjSerializer(Serializer):
            obj = ObjectField(SubSerializer)

        data = {
            "obj": {
                "field": 23
            }
        }

        s = ObjSerializer(data=data)
        self.assertRaises(ValidationError, s.validate)

    def test_validators(self):
        class EnumValidator(object):
            def __init__(self, *args):
                self.choices = args

            def validate(self, field, data):
                if data not in self.choices:
                    raise ValidationError("{} must be in {}".format(field.name, self.choices))

        class ObjSerializer(Serializer):
            enum_field = StringField(validators=[EnumValidator("hi", "bye")])

        data = {
            "enum_field": "hi",
        }

        s = ObjSerializer(data=data)
        s.validate()
        self.assertEqual(s.object.enum_field, data["enum_field"])

        data = {
            "enum_field": "Invalid Enum"
        }
        s = ObjSerializer(data=data)
        self.assertRaises(ValidationError, s.validate)

    def test_happy_path(self):
        class Obj(object):
            def __init__(self):
                self.string_field = ""
                self.integer_field = 23
                self.float_field = 2.41342
                self.boolean_field = False
                self.iso_datetime_field = datetime(2021, 2, 3, 1, 2, 3, microsecond=314498)
                self.datetime_field = datetime(2013, 5, 4, 2, 1, 0, microsecond=132832)
                self.uuid_field = None
                self.date_field = None
                self.time_field = None

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            string_field = StringField(name="stringField", required=True, allow_null=False)
            integer_field = IntegerField(name="integerField", required=True, allow_null=False)
            float_field = FloatField(name="floatField", required=True, allow_null=False)
            boolean_field = BooleanField(name="boolField", required=True, allow_null=False)
            datetime_field = DateTimeField(name="datetimeField", required=True, allow_null=False)
            iso_datetime_field = InternetDateTimeField(name="isoDatetimeField", required=True, allow_null=False)
            date_field = DateField(name="dateField", required=True, allow_null=False)
            time_field = TimeField(name="timeField", required=True, allow_null=False)
            uuid_field = UuidField(name="uuidField", required=True, allow_null=False)

        obj = Obj()
        obj.string_field = u"Some String\u2134"
        obj.integer_field = 233
        obj.float_field = 2.41342
        obj.boolean_field = True
        obj.datetime_field = datetime(2013, 5, 4, 2, 1, 0, microsecond=132832)
        obj.iso_datetime_field = datetime(2014, 8, 2, 1, 23, 51, microsecond=123143)
        obj.uuid_field = uuid.UUID("e841beb3-ff2e-4b0a-b6a6-ea56044b2288")
        obj.date_field = date(2014, 3, 1)
        obj.time_field = time(12, 30, 23, 341012)

        s = ObjSerializer(object=obj)
        s.validate()
        self.assertEqual(obj.string_field, s.data["stringField"])
        self.assertEqual(obj.integer_field, s.data["integerField"])
        self.assertEqual(obj.float_field, s.data["floatField"])
        self.assertIs(obj.boolean_field, s.data["boolField"])
        self.assertEqual("2013-05-04 02:01:00.132832", s.data["datetimeField"])
        self.assertEqual("2014-08-02T01:23:51.123143Z", s.data["isoDatetimeField"])
        self.assertEqual("e841beb3-ff2e-4b0a-b6a6-ea56044b2288", s.data["uuidField"])
        self.assertEqual("2014-03-01", s.data["dateField"])
        self.assertEqual("12:30:23.341012", s.data["timeField"])

        data = {
            "stringField": u"Some Other String \u1231",
            "integerField": 54000000000000000023434592020934082308902340823408234,
            "floatField": 200.11238237384957812938712938573945,
            "boolField": True,
            "uuidField": "e841beb3-ff2e-4b0a-b6a6-ea56044b2288",
            "datetimeField": "2013-12-30 23:56:23.431090",
            "isoDatetimeField": "2015-02-21T14:32:15.557556Z",
            "dateField": "2014-02-26",
            "timeField": "12:04:23.430123"
        }

        s2 = ObjSerializer(data=data)
        s2.validate()
        self.assertIsInstance(s2.object, Obj)
        self.assertEqual(s2.object.string_field, data["stringField"])
        self.assertEqual(s2.object.integer_field, data["integerField"])
        self.assertEqual(s2.object.float_field, data["floatField"])
        self.assertIs(s2.object.boolean_field, data["boolField"])
        self.assertEqual(uuid.UUID("e841beb3-ff2e-4b0a-b6a6-ea56044b2288"), s2.object.uuid_field)
        self.assertEqual(s2.object.datetime_field, datetime(2013, 12, 30, 23, 56, 23, 431090))
        self.assertEqual(s2.object.iso_datetime_field, datetime(2015, 2, 21, 14, 32, 15, 557556))
        self.assertEqual(s2.object.date_field, date(2014, 2, 26))
        self.assertEqual(s2.object.time_field, time(12, 4, 23, 430123))

        data = {
            "stringField": None,
            "integerField": 23,
            "floatField": 123.32
        }
        s3 = ObjSerializer(data=data)
        self.assertRaises(ValidationError, s3.validate)

        try:
            s3.validate()
        except ValidationError as ex:
            self.assertTrue(hasattr(ex, "errors"))

    def test_nullable_fields(self):
        class Obj(object):
            def __init__(self):
                self.string_field = ""

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            string_field = StringField(name="stringField", required=True, allow_null=True)

        data = {
            "stringField": None,
        }

        s2 = ObjSerializer(data=data)
        s2.validate()
        self.assertIsNone(s2.object.string_field)
        self.assertIsInstance(s2.object, Obj)

        s2 = ObjSerializer(data={})
        self.assertRaises(ValidationError, s2.validate)

    def test_missing_fields(self):
        class Obj(object):
            def __init__(self):
                self.string_field = "strfield"

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            string_field = StringField(name="stringField", required=False, allow_null=False)

        s = ObjSerializer(data={})
        s.validate()
        self.assertEqual(s.object.string_field, Obj().string_field)

    def test_default_parse_iso_datetime_string_function(self):
        cases = [("2013-04-30T12:54:23+0322", datetime(2013, 4, 30, 9, 32, 23)),
                 ("2016-12-23T23:11:34.123+0000", datetime(2016, 12, 23, 23, 11, 34, microsecond=123000)),
                 ("2016-12-23T23:11:34.123221+0000", datetime(2016, 12, 23, 23, 11, 34, microsecond=123221)),
                 ("2015-05-12T10:33:34Z", datetime(2015, 5, 12, 10, 33, 34)),
                 ("2044-02-26T13:54:11-1030", datetime(2044, 2, 27, 0, 24, 11))]
        for internet_time_string, dt in cases:
            res = _default_parse_internet_datetime_string_function(internet_time_string)
            self.assertEqual(res, dt)

    def test_internet_datetime_field(self):
        cases = [("2013-04-30T12:54:23+0322", datetime(2013, 4, 30, 12, 54, 23), timedelta(hours=3, minutes=22)),
                 ("2016-12-23T23:11:34.123+0000", datetime(2016, 12, 23, 23, 11, 34, microsecond=123000), None),
                 ("2016-12-23T23:11:34.123221+0000", datetime(2016, 12, 23, 23, 11, 34, microsecond=123221), None),
                 ("2015-05-12T10:33:34Z", datetime(2015, 5, 12, 10, 33, 34), None),
                 ("2044-02-26T13:54:11-1030", datetime(2044, 2, 26, 13, 54, 11), -timedelta(hours=10, minutes=30))]

        field = InternetDateTimeField()
        for internet_time_string, dt, offset in cases:
            offset = offset or timedelta()
            self.assertEqual(field.clean(internet_time_string), dt - offset)
        for internet_time_string, dt, offset in cases:
            est = pytz.timezone(random.choice(list(pytz.all_timezones)))
            dt = est.localize(dt)
            self.assertEqual(field.object_to_data(dt), dt.isoformat())
