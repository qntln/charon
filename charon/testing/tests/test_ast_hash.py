import pytest

import charon
import charon.testing.ast_hash

from .base import DummyClass, DummyClass2 # NOQA


@pytest.mark.parametrize('input_class, cls_hash', [
	(DummyClass, 'd2498176fad81ad017d1b0875eeeeb1b'),
	(DummyClass2, 'c3710270f679e3014e8ba3af060cf39b')
])
def test_ash_hash(input_class, cls_hash):
	assert charon.testing.ast_hash.ASTHash.get_hash(input_class) == cls_hash


def test_dumpers_version_test_missing():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()

	@test_registry.dumper(DummyClass, version = 1)
	def _load_dummy_class_v1(_):
		pass

	charon.testing.ast_hash.test_dumpers_version(charon.Codec([test_registry]))


def test_dumpers_version_test_builtin():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()

	@test_registry.dumper(set, version = 1, class_hash = 'd2498176fad81ad017d1b0875eeeeb1b')
	def _load_set_v1(_):
		pass

	charon.testing.ast_hash.test_dumpers_version(charon.Codec([test_registry]))


def test_dumpers_version_test_valid():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()

	@test_registry.dumper(DummyClass, version = 1, class_hash = 'd2498176fad81ad017d1b0875eeeeb1b')
	def _load_dummy_class_v1(_):
		pass

	charon.testing.ast_hash.test_dumpers_version(charon.Codec([test_registry]))


def test_dumpers_version_test_invalid():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()

	@test_registry.dumper(DummyClass, version = 1, class_hash = 'invalid_hash')
	def _load_dummy_class_v1(_):
		pass

	with pytest.raises(AssertionError) as e:
		charon.testing.ast_hash.test_dumpers_version(charon.Codec([test_registry]))
	assert str(e.value) == "DummyClass dumper has invalid hash 'invalid_hash', use `charon_ast_hash` to get current hash"


def test_loaders_version_test_missing():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()

	@test_registry.loader(DummyClass, version = 1)
	def _load_dummy_class_v1(_):
		pass

	charon.testing.ast_hash.test_loaders_version(charon.Codec([test_registry]))


def test_loaders_version_test_builtin():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()

	@test_registry.loader(set, version = 1, class_hash = 'd2498176fad81ad017d1b0875eeeeb1b')
	def _load_set_v1(_):
		pass

	charon.testing.ast_hash.test_loaders_version(charon.Codec([test_registry]))


def test_loaders_version_test_valid():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()

	@test_registry.loader(DummyClass, version = 1, class_hash = 'd2498176fad81ad017d1b0875eeeeb1b')
	def _load_dummy_class_v1(_):
		pass

	charon.testing.ast_hash.test_loaders_version(charon.Codec([test_registry]))


def test_loaders_version_test_invalid():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()

	@test_registry.loader(DummyClass, version = 1, class_hash = 'invalid_hash')
	def _load_dummy_class_v1(_):
		pass

	with pytest.raises(AssertionError) as e:
		charon.testing.ast_hash.test_loaders_version(charon.Codec([test_registry]))
	assert str(e.value) == "DummyClass loader has invalid hash 'invalid_hash', use `charon_ast_hash` to get current hash"
