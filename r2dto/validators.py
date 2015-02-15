from .base import ValidationError


class EnumValidator(object):
    def __init__(self, *choices):
        self.choices = choices

    def validate(self, field, data):
        if data not in self.choices:
            raise ValidationError("{} must be one of {}.  Got {}.".format(field.name, self.choices, data))
