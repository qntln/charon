import pytest

import charon.testing.generic

from .base import DummyClass, DummyClass2, test_codec # NOQA



@pytest.mark.parametrize('cls, obj', [  # NOQA
	(DummyClass2, DummyClass(1)),
	(DummyClass, DummyClass2(0)),
	(DummyClass2, DummyClass2(1)),
])
def test_generic_pipeline_test_invalid(test_codec, cls, obj):
	with pytest.raises(AssertionError):
		charon.testing.generic.test_serialization_pipeline(test_codec, cls, obj)


@pytest.mark.parametrize('cls, obj', [  # NOQA
	(DummyClass, DummyClass(1)),
	(DummyClass, DummyClass(2)),
	(DummyClass, DummyClass(41)),
])
def test_generic_pipeline_test_valid(test_codec, cls, obj):
	charon.testing.generic.test_serialization_pipeline(test_codec, cls, obj)
