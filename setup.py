# We need the following ignores because of this pylint bug: https://github.com/PyCQA/pylint/issues/73
from distutils.core import Extension, setup # pylint: disable=no-name-in-module,import-error
import os

from setuptools import find_packages



ROOT = os.path.dirname(__file__)
POSSIBLY_CYTHONIZE = [
	'charon/codec.py',
	'charon/codec_registry.py',
	'charon/extensions/standard_registry.py',
]

try:
	from Cython.Build import cythonize
	EXTENSIONS = cythonize(POSSIBLY_CYTHONIZE)
except ImportError:
	print('Not using Cython') # dumb_style_checker:disable = print-statement
	EXTENSIONS = [
		Extension(os.path.splitext(file_name)[0], [file_name.replace('.py', '.c')])
		for file_name in POSSIBLY_CYTHONIZE
		if os.path.isfile(file_name.replace('.py', '.c'))
	]


def read(relpath: str) -> str:
	with open(os.path.join(os.path.dirname(__file__), relpath)) as f:
		return f.read()


setup(
	name = 'ql-charon',
	version = open(os.path.join(ROOT, 'version.txt')).read().strip(),
	description = 'Serialization library as a replacement for pickle',
	long_description = read('README.rst'),
	author = 'Quantlane',
	author_email = 'code@quantlane.com',
	url = 'https://github.com/qntln/charon',
	install_requires = [
		'setuptools>=18.5',
		'python-dateutil>=2.4.2,<3.0.0',
		'click>=6.7,<7.0',
	],
	scripts = ['bin/charon_ast_hash'],
	packages = list(find_packages(
		include = [
			'charon',
			'charon.*'
		],
		exclude = [
			'*.tests',
		]
	)),
	ext_modules = EXTENSIONS,
	classifiers = [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: Apache Software License',
		'Natural Language :: English',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
	],
)
