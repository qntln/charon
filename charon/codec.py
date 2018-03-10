from typing import List, Any

from . import codec_registry



class Codec:
	'''
		Class used as a container for CodecRegistries,
		its main purpose is to serialize / deserialize base python types
		and call CodecRegistries for dumpable / loadable classes
	'''

	def __init__(self, registries: List[codec_registry.CodecRegistry] = None) -> None:
		self._registries = [] if registries is None else registries


	def dump(self, obj: Any) -> Any:
		dtype = type(obj) # NOQA

		if dtype in {int, float, bool, str, bytes, type(None)}:
			return obj
		elif dtype in {list, tuple}:
			return [self.dump(k) for k in obj]
		elif dtype is dict:
			return {'!meta': '!dict',
				'values': [{'key': self.dump(k), 'value': self.dump(v)} for k, v in obj.items()]
			}

		for registry in reversed(self._registries):
			if registry.dumpable(obj):
				dumped = registry.dump(obj)
				dumped['params'] = self.dump(dumped['params'])
				return dumped

		raise ValueError('Unsupported serialization object type: {dmodule}.{dtype}'.format(
			dmodule = dtype.__module__,
			dtype = dtype.__name__
		))


	def load(self, data: Any) -> Any:
		dtype = type(data) # NOQA

		if dtype in {int, float, bool, str, bytes, type(None)}:
			return data
		elif dtype in {list, tuple}:
			return [self.load(k) for k in data]
		elif dtype is dict:
			if '!meta' not in data:
				raise ValueError('Invalid dict structure')

			if data['!meta'] == '!dict':
				output = {}
				for v in data['values']:
					key = self.load(v['key'])
					value = self.load(v['value'])
					if isinstance(key, list):
						key = tuple(key)
					output[key] = value
				return output
			else:
				for registry in reversed(self._registries):
					if registry.loadable(data):
						params = self.load(data['params'])
						return registry.load(data, params)
				raise KeyError('Cannot restore object: {dtype} version: {version}'.format(
					dtype = data['!meta']['dtype'],
					version = data['!meta']['version'])
				)
		else:
			raise ValueError('Unsupported deserialization type: {dtype}'.format(dtype = dtype))
