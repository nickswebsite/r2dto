import doctest
import sys
import unittest

from tests.test_acceptance import AcceptanceTests
from tests.test_base_serializer import BaseSerializerTests

import r2dto

if __name__ == "__main__":
    doctest_ctx = {
        "Serializer": r2dto.Serializer,
        "fields": r2dto.fields,
        "ValidationError": r2dto.ValidationError,
    }

    results = doctest.testfile("../README.md", globs=doctest_ctx)
    if results.failed != 0:
        sys.exit(1)
    unittest.main()
