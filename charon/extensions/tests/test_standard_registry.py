import pytest

from charon import Codec
from charon.extensions import STANDARD_REGISTRY
from charon.testing.generic import test_serialization_pipeline # NOQA
from charon.testing.metatest import ( # NOQA
	test_charon_dumper_tests,
	test_charon_loader_tests,
	scope_charon_tests
)


pytest.fixture(scope = 'module')(scope_charon_tests)

@pytest.fixture(scope = 'module')
def serializer():
	return Codec([ STANDARD_REGISTRY ])
