import pytest

import charon
import charon.testing



class DummyClass:
	''' Dummy Class for testing simple class variable dumping and loading and versioning '''
	def __init__(self, v):
		self.version = v


class DummyClass2(DummyClass):
	pass


@pytest.fixture(scope = 'module')
def test_codec():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()


	@test_registry.dumper(DummyClass, version = 1)
	def _dump_dummy_class(obj):
		return obj.version


	@test_registry.loader(DummyClass, version = 1)
	def _load_dummy_class(data):
		return DummyClass(data)


	@test_registry.dumper(DummyClass2, version = 1)
	def _dump_dummy_class2(obj):
		return obj.version


	@test_registry.loader(DummyClass2, version = 1)
	def _load_dummy_class2(data):
		return DummyClass(data + 1)


	return charon.Codec([test_registry])
