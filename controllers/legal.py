# coding: utf8

@cache.action(time_expire=6000, cache_model=cache.ram, session=True, vars=True, public=True)
def index():
	return dict()
@cache.action(time_expire=6000, cache_model=cache.ram, session=True, vars=True, public=True)	
def privacypolicy():
	return dict()
@cache.action(time_expire=6000, cache_model=cache.ram, session=True, vars=True, public=True)	
def cookies():
	return dict()
@cache.action(time_expire=6000, cache_model=cache.ram, session=True, vars=True, public=True)	
def termandconditions():
	return dict()