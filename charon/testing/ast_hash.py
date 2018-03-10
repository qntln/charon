from typing import Any

import ast
import inspect
import hashlib
import py

import charon # NOQA



class ASTHash:
	'''
	Class for hashing ASTs of specified class,
	used for metatesting version of loaders and dumpers specific to classes

	As a hash function we use MD5, defined using class constant `_HASHING_ALGORITHM`
	'''
	_HASHING_ALGORITHM = hashlib.md5

	@classmethod
	def get_hash(cls, hcls: Any):
		'''
		Static method generating hash from supplied class,
		class is parsed using AST, from AST we generate dump which is then hashed.
		Method returns Hex digest of specified class.
		'''
		tree = ast.parse(inspect.getsource(hcls))
		dump = ast.dump(tree, annotate_fields = True, include_attributes = True)

		m = cls._HASHING_ALGORITHM()
		m.update(dump.encode('utf-8'))
		return m.hexdigest()



def test_dumpers_version(serializer: 'charon.Codec'):
	'''
	Checks whenever dumpers (with highest versions) have specified correct hash for latest version of class
	'''
	for registry in serializer._registries: # pylint: disable=protected-access
		for cls, class_hash in registry._dumpers_class_hash.items(): # pylint: disable=protected-access
			# Skip builtin classes
			if hasattr(py.builtin, cls.__name__):
				continue

			current_hash = ASTHash.get_hash(cls)
			assert class_hash == current_hash, \
				"{class_name} dumper has invalid hash '{class_hash}', use `charon_ast_hash` to get current hash".format(
				class_name = cls.__name__,
				class_hash = class_hash
			)


def test_loaders_version(serializer: 'charon.Codec'):
	'''
	Checks whenever loaders (with highest versions) have specified correct hash for latest version of class
	'''
	for registry in serializer._registries: # pylint: disable=protected-access
		for cls, class_hash in registry._loaders_class_hash.items(): # pylint: disable=protected-access
			# Skip builtin classes
			if hasattr(py.builtin, cls.__name__):
				continue

			current_hash = ASTHash.get_hash(cls)
			assert class_hash == current_hash, \
				"{class_name} loader has invalid hash '{class_hash}', use `charon_ast_hash` to get current hash".format(
				class_name = cls.__name__,
				class_hash = class_hash
			)
