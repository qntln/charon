import pytest

import charon



class DummyClass:
	''' Dummy Class for testing simple class variable dumping and loading and versioning '''
	def __init__(self, v):
		self.version = v



class DummyClass2:
	''' Dummy Class for testing missing dumper and loader '''
	pass



class EmbeddedDummyClass:
	''' Dummy Class for testing class variable dumping and loading '''
	values = [DummyClass(i) for i in range(4)] + [4 * i for i in range(4)] + [chr(i) for i in range(65, 70)] # type: ignore



@pytest.fixture(scope = 'module')
def test_codec():
	# pylint: disable=unused-variable
	test_registry = charon.CodecRegistry()


	@test_registry.dumper(EmbeddedDummyClass, version = 1)
	def _dump_embedded_dummy_class(obj):
		return obj.values


	@test_registry.loader(EmbeddedDummyClass, version = 1)
	def _load_embedded_dummy_class(obj):
		out = EmbeddedDummyClass()
		out.values = obj
		return out


	@test_registry.loader(DummyClass, version = 1)
	def _load_dummy_class_v1(_):
		return DummyClass(1)


	@test_registry.dumper(DummyClass, version = 4)
	def _dump_dummy_class_v4(_):
		return 2


	@test_registry.loader(DummyClass, version = 4)
	def _load_dummy_class_v4(_):
		return DummyClass(2)


	@test_registry.loader(DummyClass, version = 8)
	def _load_dummy_class_v8(_):
		return DummyClass(None)


	return charon.Codec([test_registry])


@pytest.fixture(scope = 'module', params = [
	4,
	4.5,
	'aa',
	[4, 5, 6],
	[4.5, 5.5, 6.5],
	['aa', 'bb', 'cc'],
])
def basic_data_type(request):
	yield request.param

@pytest.fixture(scope = 'module', params = [
	({ 1: 2, 2: 3}, {'!meta': '!dict', 'values': [{'key': 1, 'value': 2}, {'key': 2, 'value': 3}]}),
	({ 1.5: 2, 2.5: 3}, {'!meta': '!dict', 'values': [{'key': 1.5, 'value': 2}, {'key': 2.5, 'value': 3}]}),
	({'a': 'b', 'b': 'c'}, {'!meta': '!dict', 'values': [{'key': 'a', 'value': 'b'}, {'key': 'b', 'value': 'c'}]}),
	({(1, 2): [3, 4]}, {'!meta': '!dict', 'values': [{'key': [1, 2], 'value': [3, 4]}]})
])
def basic_data_dict(request):
	yield request.param

@pytest.fixture(scope = 'module', params = [
	(4, 5, 6),
	(4.5, 5.5, 6.5),
	('aa', 'bb', 'cc'),
])
def basic_data_tuple(request):
	yield request.param


def test_codec_dump_basic(basic_data_type, test_codec):
	assert test_codec.dump(basic_data_type) == basic_data_type


def test_codec_load_basic(basic_data_type, test_codec):
	assert test_codec.load(basic_data_type) == basic_data_type


def test_codec_dump_dict(basic_data_dict, test_codec):
	assert sorted(test_codec.dump(basic_data_dict[0])) == sorted(basic_data_dict[1])


def test_codec_load_dict(basic_data_dict, test_codec):
	assert test_codec.load(basic_data_dict[1]) == basic_data_dict[0]


def test_codec_dump_tuple(basic_data_tuple, test_codec):
	assert test_codec.dump(basic_data_tuple) == list(basic_data_tuple)


def test_codec_load_tuple(basic_data_tuple, test_codec):
	assert test_codec.load(basic_data_tuple) == list(basic_data_tuple)


def test_codec_dump_dummy_class(test_codec):
	assert test_codec.dump(DummyClass(1)) == {'params': 2, '!meta': {'version': 4, 'dtype': 'DummyClass'}}

	with pytest.raises(ValueError) as e:
		test_codec.dump(DummyClass2())
	assert str(e.value) == "Unsupported serialization object type: charon.tests.test_codec.DummyClass2"


def test_codec_dump_embedded_dummy_class(test_codec):
	assert test_codec.dump(EmbeddedDummyClass()) == {
		'!meta': {'dtype': 'EmbeddedDummyClass', 'version': 1},
		'params': [
			{'!meta': {'dtype': 'DummyClass', 'version': 4}, 'params': 2},
			{'!meta': {'dtype': 'DummyClass', 'version': 4}, 'params': 2},
			{'!meta': {'dtype': 'DummyClass', 'version': 4}, 'params': 2},
			{'!meta': {'dtype': 'DummyClass', 'version': 4}, 'params': 2},
			0, 4, 8, 12,
			'A', 'B', 'C', 'D', 'E'
	]}


def test_codec_dump_dummy_class_in_dict_key(test_codec):
	assert test_codec.dump({ DummyClass(1): 'a'}) == {
		'!meta': '!dict',
		'values': [{'key': {'params': 2, '!meta': {'version': 4, 'dtype': 'DummyClass'}}, 'value': 'a'}]
	}


def test_codec_dump_wrong_data_type(test_codec):
	with pytest.raises(ValueError) as e:
		test_codec.dump(EmbeddedDummyClass)
	assert str(e.value) == "Unsupported serialization object type: builtins.type"


def test_codec_load_dummy_class(test_codec):
	assert test_codec.load({'params': 1, '!meta': {'version': 1, 'dtype': 'DummyClass'}}).version == 1
	assert test_codec.load({'params': 1, '!meta': {'version': 4, 'dtype': 'DummyClass'}}).version == 2
	assert test_codec.load({'params': 1, '!meta': {'version': 8, 'dtype': 'DummyClass'}}).version is None

	with pytest.raises(KeyError) as e:
		test_codec.load({'params': 1, '!meta': {'version': 1, 'dtype': 'DummyClass2'}})
	assert str(e.value) == "'Cannot restore object: DummyClass2 version: 1'"

	with pytest.raises(KeyError) as e:
		test_codec.load({'params': 1, '!meta': {'version': 2, 'dtype': 'DummyClass'}})
	assert str(e.value) == "'Cannot restore object: DummyClass version: 2'"


def test_codec_load_embedded_dummy_class(test_codec):
	loaded = test_codec.load({
	'!meta': {'dtype': 'EmbeddedDummyClass', 'version': 1},
	'params': [
		{'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': 2},
		{'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': 2},
		{'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': 2},
		{'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': 2},
		0, 4, 8, 12,
		'A', 'B', 'C', 'D', 'E'
	]})

	assert isinstance(loaded, EmbeddedDummyClass)
	for sub in loaded.values[:4]:
		assert isinstance(sub, DummyClass)
		assert sub.version is 1

	assert loaded.values[4:] == [0, 4, 8, 12, 'A', 'B', 'C', 'D', 'E']


def test_codec_load_missing_class(test_codec):
	with pytest.raises(KeyError) as e:
		test_codec.load({
		'!meta': {'dtype': 'MissingClass', 'version': 1},
		'params': [
			{'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': 2},
			{'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': 2},
			{'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': 2},
			{'!meta': {'dtype': 'DummyClass', 'version': 1}, 'params': 2}
		]})
	assert str(e.value) == "'Cannot restore object: MissingClass version: 1'"


def test_codec_load_wrong_data_type(test_codec):
	with pytest.raises(ValueError) as e:
		test_codec.load({'a': 'b'})
	assert str(e.value) == 'Invalid dict structure'

	with pytest.raises(ValueError) as e:
		test_codec.load(EmbeddedDummyClass)
	assert str(e.value) == "Unsupported deserialization type: <class 'type'>"
