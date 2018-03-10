#
#	Note:
#	All test cases in this test file are in
#	Classes for separating test discovery within scope
#

import pytest

import charon.testing.generic
from charon import Codec, CodecRegistry
from charon.testing.metatest import (
	test_charon_loader_tests as charon_loader_tests,
	scope_charon_tests as class_tests
)



pytest.fixture(scope = 'class')(class_tests)


class TestEmptyRegistry:
	'''
	Class for testing loader metatest with empty registry
	'''

	def test_registry(self, class_tests):
		registry = CodecRegistry()
		charon_loader_tests(class_tests, Codec([ registry ]))


class TestValidRegistry:
	'''
	Class for testing loader metatests with defined test with charon mark
	'''

	@pytest.mark.ignore()
	@pytest.mark.charon(cls = int, loader_test = True)
	def test_dummy_class_loader(self):
		pass


	def test_registry(self, class_tests):
		registry = CodecRegistry()
		registry.loader(int, version = 1)
		charon_loader_tests(class_tests, Codec([ registry ]))


class TestValidGenericRegistry:
	'''
	Class for testing loader metatests with generic loader test
	'''

	@pytest.mark.ignore
	@pytest.mark.parametrize('cls, data, serializer', [ (int, (int(), ),None) ])
	def test_serialization_pipeline(self, cls, serializer, data):
		'''
		Wrapper for calling test_serialization_pipeline from charon.testing.metatest
		'''
		charon.testing.generic.test_serialization_pipeline(cls, serializer, data)


	def test_registry(self, class_tests):
		registry = CodecRegistry()
		registry.loader(int, version = 1)
		charon_loader_tests(class_tests, Codec([ registry ]))



class TestMissingRegistry:
	'''
	Class for testing loader metatests with missing test for class
	'''

	def test_registry(self, class_tests):
		registry = CodecRegistry()
		registry.loader(int, version = 1)
		with pytest.raises(AssertionError) as e:
			charon_loader_tests(class_tests, Codec([ registry ]))
		assert str(e.value) == 'Missing loader tests for: int'
