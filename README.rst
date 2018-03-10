======
Charon
======

Charon makes data serialization and deserialization simple and secure.

Charon was inspired by the `Camel project <http://camel.readthedocs.io/en/latest/camel.html>`_,
but unlike Camel it does not force a particular serialization format. Charon offers a simple interface
for defining functions that convert between complex Python objects and primitives that can be
serialized into a format of your choice.

In other words, this is not a tool that takes an object and serializes it to JSON.
It is a tool that takes an object and using a *user-defined serialization function* it converts it
to basic Python types which are then serializable to JSON, YAML, msgpack etc.

This project also contains (de)serializers for some standard types like ``datetime.datetime``,
`set`` and ``frozenset``.

Registries can be tested (see `Writing tests`_). This heavily relies on the ``pytest`` module and allows the user
to:

 * test implemented dumpers and loaders while keeping track of implemented versions (see `Version tests`_);
 * test if all dumpers and loaders have their tests (see `Metatests <#metatests-tests-testing-the-existence-of-loader-dumper-tests>`_);
 * write tests easily by simply parametrizing a predefined generalized test case (see `Generic tests`_).


Usage
=====

Define dumpers and loaders using decorators with a ``charon.CodecRegistry`` instance
and then group multiple codec registries together using ``charon.Codec``.

You can serialize and deserialize objects for which dumpers and loaders were defined by calling
the ``dump`` and ``load`` methods of ``Codec``.

Whenever a codec serializes an object, it checks what the serialization function returned and if it finds an object
that is not a basic Python type, it tries to serialize it again. This kind of recurrent behavior can be time-consuming
(and even dangerous for circular references).

.. note::

    If there are multiple registries able to serialize the same object
    with same version, the first one found from the *end* of the registries list is picked and used.

----------------
Creating dumpers
----------------

Creating a dumper is simple. First you have to create a registry in which this dumper will be stored.
This is done by:

::

    import charon

    registry = charon.CodecRegistry()


Then you just have to decorate a function which will receive an instance to serialize.
The class of the instance to serialize is given to the decorator as the first argument.
The second argument is the *version* which allows versioning of your class and its serialized structure.
This approach allows you to restore serialized objects that were created using an older structure
(field names may change, variables may come and go etc.).

The last parameter ``class_hash`` is optional and is used for version testing (see `Version tests`_).

The function that you decorate should accept one argument - the object instance to be serialized.
We serialize it into a dictionary containing base values from which we can restore this object.

.. _timedelta_dumper:

::

    @registry.dumper(datetime.timedelta, version = 1, class_hash = 'dadf350239d3779d72d9c933ab52db1b')
    def _dump_timedelta(obj):
        return {'days': obj.days, 'seconds': obj.seconds, 'microseconds': obj.microseconds}



----------------
Creating loaders
----------------

Creating a loader is also simple. Again you have to have a registry which will store this loader (we use the one defined
in the previous section), and again you have to decorate a function which will receive data,
but this time these data are those we created using the dumper function.

The loader decorator is similar to the dumper one. The first argument is the class which we should deserialize
(which we will instantiate from the data received). The second argument, version, is used as mentioned above for
versioning of the class implementation. It allows developers to change the structure of their classes and still be able
to restore previously serialized objects into this newer structure.

The function which you decorate should accept one parameter: the data previously returned by the serialization
function (see `_dump_timedelta`).
From the received dictionary we recreate an object using its constructor (if applicable) or
setting its internal variables directly (yes, this may be appropriate when deserializing data).

::

    @registry.loader(datetime.timedelta, version = 1, class_hash = 'dadf350239d3779d72d9c933ab52db1b')
    def _load_timedelta(data):
        return datetime.timedelta(days = data['days'], seconds = data['seconds'], microseconds = data['microseconds'])


-------------------------
Using loaders and dumpers
-------------------------

After we have defined all our classes which will be serialized we can use ``charon.Codec`` to serialize
and deserialize objects.

.. code:: python

    >>> import datetime
    >>> import charon, charon.extensions
    >>> codec = charon.Codec([charon.extensions.STANDARD_REGISTRY])
    >>> delta = datetime.timedelta(seconds = 42)
    >>> encoded = codec.dump(delta)
    >>> print(encoded)
    {'!meta': {'dtype': 'timedelta', 'version': 2}, 'params': [0, 42, 0]}
    >>> loaded = codec.load(encoded)
    >>> print(delta)
    0:00:42
    >>> print(loaded)
    0:00:42
    >>> print(delta == loaded)
    True

Writing tests
=============


.. note:: These tests use ``pytest`` module.

This section describes options that Charon offers for testing loaders and dumpers.
These tests are meant to help with keeping all loaders and dumpers tested and
up to date with class structure.

There is also a test function that should represent basic test structure for testing
a serialization/deserialization pipeline.

.. _pytest.mark.parametrize: https://docs.pytest.org/en/latest/parametrize.html
.. _pytest_generate_tests: https://docs.pytest.org/en/latest/parametrize.html#pytest-generate-tests

.. _generic_tests:


-------------
Generic tests
-------------

Charon contains a generic test definition ``test_serialization_pipeline``.
This test is a generalized test case consisting of object serialization, deserialization and comparison.

The original object and the deserialized object are both tested if they match the class for which the test is used.
This is a sanity check to prevent serializating instances of one class and getting instances of another class
after deserialization.

The original and the deserialized objects are then compared against each other using the ``vars`` function
if possible, otherwise the standard equality operator (``__eq__``) is used.

Usage
-----

First you have to import the appropriate test function. This is best done in ``conftest.py`` because we will use it later.
You also have to define a ``serializer`` fixture to use with this test.

::

    import pytest

    import charon
    from charon.testing.generic import test_serialization_pipeline


    @pytest.fixture
    def serializer():
        return charon.Codec([registry])


Then you have to define parameters.
You can rename the test function to some convenient name and then use a wrapper to call it.
But it is better to parametrize it directly using the pytest marker `pytest.mark.parametrize`_:

::

    pytest.mark.parametrize([(ExampleClass, ExampleClass('Ahoy'))])(test_serialization_pipeline)



Another way to parametrize it is by using the `pytest_generate_tests`_ function of pytest.

::

    def pytest_generate_tests(metafunc):
        '''
        Generates test cases for simple deserialization and serialization.
        Test cases are generated by functions with ```generate_``` prefix
        '''
        if metafunc.function.__name__ == 'test_serialization_pipeline':
            metafunc.parametrize('cls, original_obj', [(ExampleClass, ExampleClass('Ahoy'))])

.. _Metatests:

--------------------------------------------------------------
Metatests - Tests testing the existence of loader/dumper tests
--------------------------------------------------------------

Charon contains tests for testing whenever all dumpers and loaders have tests. This aproach is called metatesting.

These tests are convenient when you want to make sure that all of your dumpers and loaders have tests.


Usage
-----


To use this metatest you have to mark your dumper and loader tests with ``pytest.mark``.

.. code:: python

    @pytest.mark.charon(cls = ExampleClass, dumper_test = True, loader_test = False)
    def test_example_dumper(self):
       pass

As you can see you use keywords to set up the mark. The ``cls`` keyword specifies the class for which this test works,
``dumper_test`` specifies if this is a dumper test and obviously ``loader_test`` specifies whenever this is a loader test.

This way you mark all of your tests. Then you just have to import metatests from the ``charon.testing.metatest`` package.

.. code:: python

    from charon.testing.metatest import (
        test_charon_dumper_tests,
        test_charon_loader_tests,
        scope_charon_tests
    )

    pytest.fixture(scope = 'module')(scope_charon_tests)



And that's all: from this point forth all loader and dumper methods would have to be properly tested.

.. note:: This only tests the existence of tests. It does not test the version for which those teste were written. To test the version for which the tests were written see `Version tests`_.

.. note::

    pytest.fixture(scope = 'module')(scope_charon_tests)

    We create this fixture in the module scope and in the session scope because that could create false positive cases.
    Example:
        You have have two registries in different codecs which serialize and deserialize the same class differently.
        One of these codecs have tests for this class and the others don't. If you use a session fixture in this case
        you will get a false positive check, because the fixture will return tests which are defined for one of the codecs
        but not for the other. Metatests do not check to which codec (implementation) is a test bound.


.. _version_tests:

-------------
Version tests
-------------

In large projects it is sometimes difficult to keep track of changes in classes, and to keep their serialization up to date.
For example, in a project with multiple people colaborating on it changes in one class can be made separatwly by multiple
developers, and one of them may forget to update the particular dumpers and loaders and increment their version.

To prevent this, Charon has an option to create a hash of class implementation (hash of the AST) and annotate
a dumper / loader with it. Charon also includes tests from ``charon.testing.ast_hash`` called
``test_dumpers_version``
and ``test_loaders_version``.

Usage
-----

To use this feature first we have to create a hash of the current implementation.
This can be done using ``charon_ast_hash`` script provided by this package.
See: ``Generating a hash``

When we havea  hash of the class implementation we add a keyword to the standard decorator for loader / dumper.

.. code:: python

    @registry.dumper(Object, version = 1, class_hash = 'd2498176fad81ad017d1b0875eeeeb1b')
    def _load_object_v1(_):
        pass

This way we pass the hash of the class implementation to the registry.

.. note::

    The hash is kept only for the latest version of a dumper / loader because
    we cannot check these versions with older implementations of a particular class.

These are all the changes in dumper and loader implementations. Next you have to import the test methods
`charon.testing.ast_hash.test_dumpers_version`` and ``charon.testing.ast_hash.test_loaders_version``
into your test file and pass it an instance of ``charon.Codec``, containing the registries you want to test.

.. code:: python

    from charon.testing.ast_hash import test_dumpers_version, test_loaders_version

    @pytest.fixture
    def serializer():
        return charon.Codec([my_registry])


From this point on, whenever you run pytest, all your loaders and dumpers which have ``class_hash`` defined will be
checked against the hash of the current class implementation.


.. _generating-class-hash:

---------------------------------------------
Generating a hash of a class implementation
---------------------------------------------

To generate the hash of the AST (Abstract Syntax Tree) of a class you can use script provided with Charon
called ``charon_ast_hash``. This script takes a list of classes to be hashed as an argument list.

.. note::

    This command internally uses the ``inspect`` module to get the source code which is then parsed by the ``ast`` module.
    Methods and classes from ``__builtins__`` and from compiled libraries cannot be hashed.


Example usage
--------------
.. code:: bash

   $ charon_ast_hash  datetime.datetime datetime.time
   datetime.datetime: 4927808ca19f2a1494719baa11024a7d
   datetime.time: c36b819f18698ee9143ecd92e3788c66

Standard Registry
=================

The Charon package comes with an implementation for some Python types that are built in or in the standard library:

* ``decimal.Decimal``
* ``set``
* ``frozenset``
* ``datetime.datetime``
* ``datetime.date``
* ``datetime.time``
* ``datetime.timedelta``

This registry can be used by simply creating your ``charon.codec`` with an additional registry
``charon.extensions.STANDARD_REGISTRY``.



-------------
Example usage
-------------

Basic usage is pretty simple. You just have to create a ``charon.codec`` object with an additional codec registry
``charon.extensions.STANDARD_REGISTRY``,
preferably at the begining of the list (in case you would want to override standard implementations of dumpers / loaders).

.. code:: python

    >>> import charon, charon.extensions
    >>> import decimal
    >>> codec = charon.Codec([charon.extensions.STANDARD_REGISTRY])
    >>> number = decimal.Decimal('4.5')
    >>> print(number)
    4.5
    >>> serialized = codec.dump(number)
    >>> print(serialized)
    {'!meta': {'dtype': 'Decimal', 'version': 1}, 'params': '4.5'}
    >>> loaded = codec.load(serialized)
    >>> print(loaded)
    4.5
