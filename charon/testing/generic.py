import charon # NOQA



def test_serialization_pipeline(serializer: 'charon.Codec', cls, original_obj):
	'''
	This is generic test for serialization pipeline which takes as an argument class to which is this test bound,
	serializer which should be able to serialize and deserialize the class,
	and original object instance use as a test case parameter.
	This object instance is serialized, and then deserialized,
	resulting object is compared against supplied one
	'''
	serialized = serializer.dump(original_obj)
	loaded = serializer.load(serialized)

	assert isinstance(original_obj, cls) # sanity check
	assert isinstance(loaded, cls)
	if '__dict__' in dir(loaded):
		assert vars(loaded) == vars(original_obj)
	else:
		assert loaded == original_obj
