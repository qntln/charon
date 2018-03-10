from typing import Set # NOQA

import charon # NOQA



def charon_marked_test(test) -> bool:
	'''
	Filter function for selecting only tests relevant to charon dumpers and loaders.
	These tests have charon marker with class definition and flag indicating if it is loader or dumper test (or both).
	Or generic tests imported from charon package which names are `test_dumper_generic` and `test_loader_generic`
	'''
	name = test.function.__name__
	marker = test.get_marker('charon')

	return (
		(
			marker and
			'cls' in marker.kwargs and
			len(set(marker.kwargs.keys()) & { 'dumper_test', 'loader_test' }) > 0
		) or
		name in [ 'test_serialization_pipeline' ]
	)


def get_tests(obj):
	'''
	This function collects tests from internal pytest structures using 'collect' method
	'''
	if 'items' in vars(obj):
		return obj.items
	elif 'collect' in dir(obj):
		output = []
		for item in obj.collect():
			tests = get_tests(item)
			if isinstance(tests, list):
				output += tests
			else:
				output += [ tests ]
		return output
	return obj


def scope_charon_tests(request):
	'''
	This function returns list of all dumper and loader tests
	defined in current scope (session, module, class, etc) related to charon.
	Use this function like:
	  `pytest.fixture(scope = 'desired_scope')(scope_charon_tests)`
	'''
	return list(filter(charon_marked_test, get_tests(request.node)))



def test_charon_dumper_tests(scope_charon_tests, serializer: 'charon.Codec'):
	'''
	Test to check whenever all classes that is serializer able to **dump** have tests
	'''
	serialization_tests = set()
	for test in scope_charon_tests:
		marker = test.get_marker('charon')

		# Check if charon marker exists and if it is relevant to serialization
		if marker and marker.kwargs.get('dumper_test', False):
			cls = marker.kwargs['cls']
		# Check name for generic dumper test
		elif test.function.__name__ == 'test_serialization_pipeline':
			cls = test.callspec.params['cls']
		else:
			continue

		serialization_tests.add(cls.__name__)

	all_serializable = set() # type: Set[str]
	for registry in serializer._registries: # pylint: disable=protected-access
		all_serializable.update(registry._dumpers.keys()) # pylint: disable=protected-access

	missing_tests = all_serializable - (serialization_tests & all_serializable)
	assert not missing_tests, 'Missing dumper tests for: ' + ', '.join(missing_tests)


def test_charon_loader_tests(scope_charon_tests, serializer: 'charon.Codec'):
	'''
	Test to check whenever all classes that is serializer able to **load** have tests
	'''
	deserialization_tests = set()
	for test in scope_charon_tests:
		marker = test.get_marker('charon')

		# Check if charon marker exists and if it is relevant to serialization
		if marker and marker.kwargs.get('loader_test', False):
			cls = marker.kwargs['cls']
		# Check name for generic dumper test
		elif test.function.__name__ == 'test_serialization_pipeline':
			cls = test.callspec.params['cls']
		else:
			continue

		deserialization_tests.add(cls.__name__)

	all_deserializable = set() # type: Set[str]
	for registry in serializer._registries: # pylint: disable=protected-access
		all_deserializable.update(registry._loaders.keys()) # pylint: disable=protected-access

	missing_tests = all_deserializable - (deserialization_tests & all_deserializable)
	assert not missing_tests, 'Missing loader tests for: ' + ', '.join(missing_tests)
