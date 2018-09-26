# coding: utf8
@cache.action(time_expire=6000, cache_model=cache.ram, session=True, vars=True, public=True)
def index():
	return dict()