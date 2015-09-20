def ModelIt(fromUser = 'Default', brewery = 'Insight'):
	print 'The brewery is %s' %brewery
	result = len(brewery)*100
	if fromUser != 'Default':
		return result
	else:
		return 'check your input'