#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import DIV, LI, A, UL, URL, XML
# import logging
# logger = logging.getLogger(" >>>> modules/pagination >>>> GestionExperta: ")
# logger.setLevel(logging.DEBUG)

class Pagination(DIV):

	def __init__(self, records, items_per_page):
		self.records=records
		self.items_per_page=items_per_page
		
	def limitby(self):
		from gluon import current 
		page = self.page=int(current.request.vars.page or 0) 
		return (self.items_per_page*page,self.items_per_page*(page+1)) 


	def xml(self): 
		from gluon import current 
		pages,rem = divmod(self.records,self.items_per_page)
		li=[]
		if rem: pages+=1 
		if self.page>0:
			li.append(LI(A(XML('<i class="glyphicon glyphicon-fast-backward"></i>'),_href=URL(args=current.request.args,vars=dict(page=0)))))
		else:
			li.append(LI(A(XML('<i class="glyphicon glyphicon-fast-backward"></i>'),_href="#"), _class="disabled"))
		if self.page>=1:
			li.append(LI(A(XML('<i class="glyphicon glyphicon-backward"></i>'),_href=URL(args=current.request.args,vars=dict(page=self.page-1)))))
		else:
			li.append(LI(A(XML('<i class="glyphicon glyphicon-backward"></i>'),_href="#"), _class="disabled"))

		li.append(LI(A(XML('<i class="glyphicon glyphicon-file"></i>Página %s de %s'% (self.page+1, int(self.records/self.items_per_page)+1))), _class="disabled"))

		if self.page<=pages-2:
			li.append(LI(A(XML('<i class="glyphicon glyphicon-forward"></i>'),_href=URL(args=current.request.args,vars=dict(page=self.page +1))), _class="next"))
		else:
			li.append(LI(A(XML('<i class="glyphicon glyphicon-forward"></i>'),_href="#"), _class="disabled"))
		if self.page<pages-1:
			li.append(LI(A(XML('<i class="glyphicon glyphicon-fast-forward"></i>'),_href=URL(args=current.request.args,vars=dict(page=pages-1)))))
		else:
			li.append(LI(A(XML('<i class="glyphicon glyphicon-fast-forward"></i>'),_href="#"), _class="disabled"))
		div=DIV(UL(li,_class="pagination  pagination-sm") )
		return DIV.xml(div)