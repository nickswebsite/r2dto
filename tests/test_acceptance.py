import unittest

from r2dto.fields import StringField, BooleanField, FloatField, IntegerField, ListField, ObjectField
from r2dto import Serializer, ValidationError


class AcceptanceTests(unittest.TestCase):
    def test_complex_types(self):
        class SubObj(object):
            def __init__(self):
                self.field = "Field One"

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

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            string_field = StringField(name="stringField", required=True, allow_null=False)
            integer_field = IntegerField(name="integerField", required=True, allow_null=False)
            float_field = FloatField(name="floatField", required=True, allow_null=False)
            boolean_field = BooleanField(name="boolField", required=True, allow_null=False)

        obj = Obj()
        obj.string_field = u"Some String\u2134"
        obj.integer_field = 233
        obj.float_field = 2.41342
        obj.boolean_field = True

        s = ObjSerializer(object=obj)
        s.validate()
        self.assertEqual(obj.string_field, s.data["stringField"])
        self.assertEqual(obj.integer_field, s.data["integerField"])
        self.assertEqual(obj.float_field, s.data["floatField"])
        self.assertIs(obj.boolean_field, s.data["boolField"])

        data = {
            "stringField": u"Some Other String \u1231",
            "integerField": 54000000000000000023434592020934082308902340823408234,
            "floatField": 200.11238237384957812938712938573945,
            "boolField": True,
            }

        s2 = ObjSerializer(data=data)
        s2.validate()
        self.assertIsInstance(s2.object, Obj)
        self.assertEqual(s2.object.string_field, data["stringField"])
        self.assertEqual(s2.object.integer_field, data["integerField"])
        self.assertEqual(s2.object.float_field, data["floatField"])
        self.assertIs(s2.object.boolean_field, data["boolField"])

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
