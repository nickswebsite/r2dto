import doctest
import sys
import unittest

import r2dto
from tests.test_acceptance import AcceptanceTests
from tests.test_base_serializer import BaseSerializerTests

__all__ = ["doctest", "sys", "unittest", "r2dto", "AcceptanceTests", "BaseSerializerTests"]

try:
    import pep8
except ImportError:
    print("WARNING: pep8 not installed.  Style will not be checked and therefore your build may fail when integrated"
          "with the main branch.")
    pep8 = None

PEP8_SOURCES = [
    "r2dto/__init__.py",
    "r2dto/base.py",
    "r2dto/fields.py",
    "r2dto/validators.py",
    "tests/__init__.py",
    "tests/__main__.py",
    "tests/test_acceptance.py",
    "tests/test_base_serializer.py",
]

if __name__ == "__main__":
    if pep8 is not None:
        sg = pep8.StyleGuide(max_line_length=120)
        res = sg.check_files(PEP8_SOURCES)
        if res.total_errors != 0:
            print("pep8 failed")
            sys.exit(1)

    doctest_ctx = {
        "Serializer": r2dto.Serializer,
        "fields": r2dto.fields,
        "ValidationError": r2dto.ValidationError,
    }

    results = doctest.testfile("../README.md", globs=doctest_ctx)
    if results.failed != 0:
        sys.exit(1)
    unittest.main()
