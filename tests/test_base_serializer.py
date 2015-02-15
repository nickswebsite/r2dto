import unittest

from r2dto.fields import StringField
from r2dto import Serializer


class BaseSerializerTests(unittest.TestCase):
    def test_metaclass_creation(self):
        class ObjSerializer(Serializer):
            string_field = StringField(name="stringField", required=True, allow_null=False)

        for field in ObjSerializer.fields:
            self.assertIs(field.parent, ObjSerializer)

    def test_ctor(self):
        class ObjSerializer(Serializer):
            string_field = StringField(name="stringField", required=True, allow_null=False)

        obj = object()
        s = ObjSerializer(object=obj)
        self.assertIs(s.object, obj)
        self.assertIsNone(s.data)

        data = {}
        s = ObjSerializer(data=data)
        self.assertIs(s.data, data)
        self.assertIsNone(s.object)

    def test_data_to_object(self):
        class Obj(object):
            def __init__(self):
                self.string_field = "Some String Value"

        class ObjSerializer(Serializer):
            class Meta:
                model = Obj

            string_field = StringField(name="stringField", required=True, allow_null=False)

        data = {"stringField": "Some String Value"}

        s = ObjSerializer(data=data)
        s.data_to_object()
        self.assertEqual(data["stringField"], s.object.string_field)
        self.assertIsInstance(s.object, Obj)

    def test_object_to_data(self):
        class ObjSerializer(Serializer):
            string_field = StringField(name="stringField", required=True, allow_null=False)

        class Obj(object):
            def __init__(self):
                self.string_field = "Some String Value"

        o = Obj()
        s = ObjSerializer(object=o)
        s.object_to_data()
        self.assertEqual(s.data["stringField"], o.string_field)

    def test_validate_data_to_object(self):
        class ObjSerializer(Serializer):
            string_field = StringField(name="stringField", required=True, allow_null=False)

        data = {"stringField": "Some String Value"}

        s = ObjSerializer(data=data)
        s.validate()
        self.assertEqual(data["stringField"], s.object.string_field)

    def test_validate_object_to_data(self):
        class Obj(object):
            def __init__(self):
                self.string_field = "Some String Value"

        class ObjSerializer(Serializer):
            string_field = StringField(name="stringField", required=True, allow_null=False)

        o = Obj()

        s = ObjSerializer(object=o)
        s.validate()
        self.assertEqual(s.data["stringField"], o.string_field)
