#
#	Note:
#	All test cases in this test file are in
#	Classes for separating test discovery within scope
#

import pytest

import charon.testing.generic
from charon import Codec, CodecRegistry
from charon.testing.metatest import (
	test_charon_dumper_tests as charon_dumper_tests,
	scope_charon_tests as class_tests
)



pytest.fixture(scope = 'class')(class_tests)


class TestEmptyRegistry:
	'''
	Class for testing dumper metatest with empty registry
	'''

	def test_registry(self, class_tests):
		registry = CodecRegistry()
		charon_dumper_tests(class_tests, Codec([ registry ]))


class TestValidRegistry:
	'''
	Class for testing dumper metatests with defined test with charon mark
	'''

	@pytest.mark.ignore()
	@pytest.mark.charon(cls = int, dumper_test = True)
	def test_dummy_class_dumper(self):
		pass


	def test_registry(self, class_tests):
		registry = CodecRegistry()
		registry.dumper(int, version = 1)
		charon_dumper_tests(class_tests, Codec([ registry ]))


class TestValidGenericRegistry:
	'''
	Class for testing dumper metatests with generic dumper testing.metatest
	'''

	@pytest.mark.ignore
	@pytest.mark.parametrize('cls, data, serializer', [ (int, (int(),), None) ])
	def test_serialization_pipeline(self, cls, serializer, data):
		'''
		Wrapper for calling test_serialization_pipeline from charon.testing.metatest
		'''
		charon.testing.generic.test_serialization_pipeline(cls, serializer, data)


	def test_registry(self, class_tests):
		registry = CodecRegistry()
		registry.dumper(int, version = 1)
		charon_dumper_tests(class_tests, Codec([ registry ]))



class TestMissingRegistry:
	'''
	Class for testing dumper metatests with missing test for class
	'''

	def test_registry(self, class_tests):
		registry = CodecRegistry()
		registry.dumper(int, version = 1)
		with pytest.raises(AssertionError) as e:
			charon_dumper_tests(class_tests, Codec([ registry ]))
		assert str(e.value) == 'Missing dumper tests for: int'
