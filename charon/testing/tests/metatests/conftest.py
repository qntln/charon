def pytest_collection_modifyitems(session, config, items): # pylint: disable=unused-argument
	'''
	Removes tests which are marked with **ignore** marker
	'''
	marked = []
	keep = []
	for item in items:
		if item.get_marker('ignore'):
			marked.append(item)
		else:
			keep.append(item)

	config.hook.pytest_deselected(items = marked)
	items[:] = keep
