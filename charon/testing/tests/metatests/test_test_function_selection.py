import pytest

from charon.testing.metatest import charon_marked_test



@pytest.mark.ignore()
@pytest.mark.noncharon()
def test_other_marked():
	pass


@pytest.mark.ignore()
@pytest.mark.charon()
def test_marked_invalid():
	pass


@pytest.mark.ignore()
@pytest.mark.charon(cls = None)
def test_marked_invalid2():
	pass


@pytest.mark.ignore()
@pytest.mark.charon(dumper_test = True)
def test_marked_invalid3():
	pass


@pytest.mark.ignore()
@pytest.mark.charon(loader_test = True)
def test_marked_invalid4():
	pass


@pytest.mark.ignore()
@pytest.mark.charon(dumper_test = True, loader_test = True)
def test_marked_invalid5():
	pass


@pytest.mark.ignore()
@pytest.mark.charon(cls = None, dumper_test = True)
def test_marked_valid1():
	pass


@pytest.mark.ignore()
@pytest.mark.charon(cls = None, loader_test = True)
def test_marked_valid2():
	pass


@pytest.mark.ignore()
@pytest.mark.charon(cls = None, dumper_test = True, loader_test = True)
def test_marked_valid3():
	pass


@pytest.fixture(scope = 'module')
def all_tests(request):
	'''
	Generate list of all tests within this module
	'''
	session = request.node
	return session.collect()


def test_selection(all_tests):
	valid_tests = list(filter(charon_marked_test, all_tests))
	for test in valid_tests:
		assert test.function.__name__.startswith('test_marked_valid')
