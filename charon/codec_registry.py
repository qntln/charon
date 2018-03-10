from typing import Any

import collections
import functools

from . import types



class DuplicateVersion(ValueError):
	'''
	Exception thrown when user is trying to register another dumper or loader
	for same class and version
	'''
	pass



class CodecRegistry:
	'''
	Class used for registering new dumpers and loaders for classes using function decorators
	'''
	def __init__(self):
		self._dumpers = collections.defaultdict(dict) # type: Dict[str, Any]
		self._loaders = collections.defaultdict(dict) # type: Dict[str, Any]

		self._dumpers_class_hash = collections.defaultdict(dict) # type: Dict[Any, str]
		self._loaders_class_hash = collections.defaultdict(dict) # type: Dict[Any, str]


	def dumper(self, cls: Any, version: types.VersionType, class_hash: str = None) -> types.CoderType:
		'''
		Decorator checks version type, then checks for already saved dumper for specific class and version,
		if passes saves it for specific class and version,

		If class hash is specified it is checked if it is string, and if so, it is registered based on version.
		Only highest version of class hash is kept because we cannot check hash of older class implementation.
		Class hash set to None is ignored, this is feature used for compatibility.
		'''
		if not isinstance(version, int):
			raise ValueError('Version must be integer, not: {vtype}'.format(vtype = type(version).__name__))

		if class_hash is not None and not isinstance(class_hash, str):
			raise ValueError('Class hash must be string or None, not: {vtype}'.format(vtype = type(class_hash).__name__))

		if version in self._dumpers[cls.__name__]:
			raise DuplicateVersion

		highest_version = max(self._dumpers[cls.__name__]) if self._dumpers[cls.__name__] else None
		# Keep class hash only for dumper with highest version, we cannot check hash of older versions
		if class_hash and (not highest_version or version > highest_version):
			self._dumpers_class_hash[cls] = class_hash

		def decorator(f):
			self._dumpers[cls.__name__][version] = functools.partial(self._run_representer, f)

		return decorator

	@staticmethod
	def _run_representer(representer: types.CoderType, data: Any) -> types.BaseType:
		canonic_value = representer(data)
		canonic_type = type(canonic_value) # NOQA

		if canonic_type in {int, float, bool, str, bytes, type(None), list, tuple, dict}:
			return canonic_value
		else:
			raise TypeError('Dumpers must return python native type, not {dtype!r}'.format(dtype = canonic_type.__name__))


	def dump(self, obj: Any) -> types.EncodingType:
		'''
		This method is private to project, and should be NEVER used outside of it. Use Codec([registry]).dump instead.

		Method checks if specified object type has dumper,
		dumper version is selected as a highest available for specified dumper,
		then creates Dict containing metadata about class and class parameters returned by dumper
		'''
		dtype = type(obj) # NOQA

		if dtype.__name__ not in self._dumpers:
			raise KeyError('Cannot dump object of type: {dtype} missing dumper'.format(dtype = dtype.__name__))

		class_dumpers = self._dumpers[dtype.__name__]
		available_versions = list(sorted(class_dumpers.keys()))
		selected_version = available_versions[-1]

		return {
			'!meta': { 'dtype': dtype.__name__, 'version': selected_version },
			'params': class_dumpers[selected_version](obj)
		}


	def dumpable(self, obj: Any) -> bool:
		dtype = type(obj) # NOQA
		return dtype.__name__ in self._dumpers


	def loader(self, cls: Any, version: types.VersionType, class_hash: str = None) -> types.CoderType:
		'''
		Decorator checks for already saved loader for specific class and version,
		if passes saves it for specific class and version

		If class hash is specified it is checked if it is string, and if so, it is registered based on version.
		Only highest version of class hash is kept because we cannot check hash of older class implementation.
		Class hash set to None is ignored, this is feature used for compatibility.
		'''
		if not isinstance(version, int):
			raise ValueError('Version must be integer, not: {vtype}'.format(vtype = type(version).__name__))

		if class_hash is not None and not isinstance(class_hash, str):
			raise ValueError('Class hash must be string or None, not: {vtype}'.format(vtype = type(class_hash).__name__))

		if version in self._loaders[cls.__name__]:
			raise DuplicateVersion

		highest_version = max(self._loaders[cls.__name__]) if self._loaders[cls.__name__] else None
		# Keep class hash only for loader with highest version, we cannot check hash of older versions
		if class_hash and (not highest_version or version > highest_version):
			self._loaders_class_hash[cls] = class_hash

		def decorator(f):
			self._loaders[cls.__name__][version] = f

		return decorator


	def loadable(self, data: types.EncodingType) -> bool:
		metadata = data['!meta']
		dtype = metadata['dtype']
		version = metadata['version']

		if dtype not in self._loaders:
			return False

		if not isinstance(version, int):
			raise ValueError('Invalid version type: {vtype} version: {version}'.format(
				vtype = type(version).__name__, version = version)
			)

		return version in self._loaders[dtype]


	def load(self, data: types.EncodingType, params: Any) -> Any:
		'''
		This method is private to project, and should be NEVER used outside of it. Use Codec([registry]).load instead.

		Method checks if specified object type has loader,
		loader version is selected as specified version or 'None' if loader for specified version does not exist,
		returns result of selected loader call with saved class data
		'''
		metadata = data['!meta']
		dtype = metadata['dtype']
		version = metadata['version']

		if dtype not in self._loaders:
			raise KeyError('Cannot load object of type: {dtype} missing loader'.format(dtype = dtype))

		loaders = self._loaders[dtype]

		if not isinstance(version, int):
			raise ValueError('Invalid version type: {vtype} version: {version}'.format(
				vtype = type(version).__name__, version = version)
			)

		if version not in loaders:
			raise KeyError('Missing apropriate loader for class {dtype} with version: {version}'.format(
				dtype = dtype, version = version)
			)

		return loaders[version](params)
