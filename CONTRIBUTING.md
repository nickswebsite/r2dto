Contributing
============

This project is open to contributions from other authors, though please note that the license is Public Domain and
should continue to remain that way.

Guidelines
----------

* Don't add extra dependencies.  (I actually went out of my way to not even include `six`.)
* Stick to PEP-8 (There is actually a test to ensure that pep8 is adhered to.)
* Make sure tests pass before submitting a pull request.
* If adding a new feature, a new acceptance test should be written.
* When adding a new field, make sure you can't do the same thing with a validator.  Fields should correspond to an
  underlying type or class.  Try to do the same thing with a validator rather than introducing a new field.
* Documentation should usually have doctests.

Getting Started
---------------

You will need python2.7, python3.2, python3.3, python3.4, pypy, and pypy3 installed and on your PATH.

Usually I use a virtualenv setup with python 2.7.

    virtualenv v

    . v/bin/activate

Tox is needed to run the tests:

    pip install tox

Then to run the tests, simply run:

    tox

Todos
-----

* More tests need to be written, particularly for fields.
* Implement TimestampField.
* Implement EmailValidator.
* Implement UrlValidator.
* Set up tox to test with pypy and pypy3 (already integrated with travis-ci.)
