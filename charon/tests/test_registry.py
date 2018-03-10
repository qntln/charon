import pytest

import charon



class DummyClass:
	''' Dummy Class for testing simple class variable dumping and loading and versioning '''
	def __init__(self, data = None):
		self.data = data



@pytest.fixture(scope = 'module')
def test_registry():
	# pylint: disable=unused-variable
	registry = charon.CodecRegistry()


	@registry.dumper(charon.CodecRegistry, version = 1)
	def _dump_codec_registry(data):
		return data


	@registry.loader(charon.CodecRegistry, version = 1)
	def _load_codec_registry(data):
		return data


	@registry.dumper(DummyClass, version = 1)
	def _dump_dummy_class(obj):
		return obj.data


	@registry.loader(DummyClass, version = 1)
	def _load_dummy_class(data):
		return DummyClass(data)


	return registry


def test_codec_registry_add_dumper(test_registry):
	assert test_registry.dumpable(charon.CodecRegistry()) is True
	assert test_registry.dumpable(charon.Codec()) is False


def test_codec_registry_dumper_duplicate():
	registry = charon.CodecRegistry()

	with pytest.raises(charon.DuplicateVersion):
		@registry.dumper(charon.CodecRegistry, version = 1)
		def _d(data):
			return data

		@registry.dumper(charon.CodecRegistry, version = 1)
		def _d2(data):
			return data


def test_codec_registry_invalid_dumper_version():
	registry = charon.CodecRegistry()
	with pytest.raises(ValueError) as e:
		@registry.dumper(charon.CodecRegistry, version = 'a')
		def _d(data):
			return data
	assert str(e.value) == 'Version must be integer, not: str'


def test_codec_registry_invalid_dumper(test_registry):
	with pytest.raises(TypeError) as e:
		test_registry.dump(test_registry)

	assert str(e.value) == "Dumpers must return python native type, not 'CodecRegistry'"


def test_codec_registry_missing_dumper(test_registry):
	with pytest.raises(KeyError) as e:
		test_registry.dump(charon.Codec())

	assert str(e.value) == "'Cannot dump object of type: Codec missing dumper'"


def test_codec_registry_dump(test_registry):
	assert test_registry.dump(DummyClass()) == {'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': None}


def test_codec_registry_dump_extended(test_registry):
	params = {'a': 'b'}

	dumped = test_registry.dump(DummyClass(params))
	assert dumped == {'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': params}


def test_codec_registry_add_loader(test_registry):
	assert test_registry.loadable({'!meta': {'dtype': 'CodecRegistry', 'version': 1} , 'params': None}) is True
	assert test_registry.loadable({'!meta': {'dtype': 'Codec', 'version': 1} , 'params': None}) is False


def test_codec_registry_loader_duplicate():
	registry = charon.CodecRegistry()


	@registry.loader(charon.CodecRegistry, version = 1)
	def _d(data):
		return data

	with pytest.raises(charon.DuplicateVersion):
		@registry.loader(charon.CodecRegistry, version = 1)
		def _d2(data):
			return data


def test_codec_registry_invalid_loader_version():
	registry = charon.CodecRegistry()
	with pytest.raises(ValueError) as e:
		@registry.loader(charon.CodecRegistry, version = 'a')
		def _d(data):
			return data
	assert str(e.value) == 'Version must be integer, not: str'


def test_codec_registry_missing_loader(test_registry):
	with pytest.raises(KeyError) as e:
		test_registry.load({'!meta': {'dtype': 'Codec', 'version': 1} , 'params': None}, None)
	assert str(e.value) == "'Cannot load object of type: Codec missing loader'"


def test_codec_registry_missing_loader_version(test_registry):
	with pytest.raises(KeyError) as e:
		test_registry.load({'!meta': {'dtype': 'CodecRegistry', 'version': 2} , 'params': None}, None)
	assert str(e.value) == "'Missing apropriate loader for class CodecRegistry with version: 2'"


def test_codec_registry_load(test_registry):
	assert isinstance(test_registry.load({'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': None}, None), DummyClass)


def test_codec_registry_load_extended(test_registry):
	params = {'a': 'b'}
	loaded = test_registry.load({'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': params}, params)

	assert isinstance(loaded, DummyClass)
	assert loaded.data == params


def test_codec_registry_load_missing_metadata(test_registry):
	with pytest.raises(KeyError):
		test_registry.loadable({'params': None})

	with pytest.raises(KeyError):
		test_registry.load({'params': None}, None)


def test_codec_registry_load_invalid_version_type(test_registry):
	with pytest.raises(ValueError) as e:
		test_registry.loadable({'!meta': {'dtype': 'DummyClass', 'version': '4.5'}, 'params': None})
	assert str(e.value) == 'Invalid version type: str version: 4.5'


	with pytest.raises(ValueError) as e:
		test_registry.load({'!meta': {'dtype': 'DummyClass', 'version': '4.5'}, 'params': None}, None)
	assert str(e.value) == 'Invalid version type: str version: 4.5'


def test_codec_registry_load_missing_loader(test_registry):
	with pytest.raises(KeyError) as e:
		test_registry.load({'!meta': {'dtype': 'Codec', 'version': 1}, 'params': None}, None)
	assert str(e.value) == "'Cannot load object of type: Codec missing loader'"
