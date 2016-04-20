# -*- coding: utf-8 -*-
import math, urllib, json, time
from openerp import models, fields, api
class uis_papl_transformation(models.Model):
	_name='uis.papl.transformer'
	_description='Transformer'
	name=fields.Char(string='Name')
	apl_id=fields.Many2one('uis.papl.apl', string='APL Name')
	tap_id=fields.Many2one('uis.papl.tap', string='Tap Name')
	pillar_id=fields.Many2one('uis.papl.pillar',string='Pillar Name', domain="[('id','in',str_pillar_ids)]")
	longitude=fields.Float(digits=(2,6), string='Longitude')
	latitude=fields.Float(digits=(2,6), string='Latitude')
	#near_pillar_ids=fields.Many2one('uis.papl.pillar', string='Near pillars ids', compute='_get_near_pillar')
	str_pillar_ids=fields.Char(string="pillar ids str", compure='_get_near_pillar')
	near_pillar_ids=fields.Many2many('uis.papl.pillar',
									 relation='near_pillar_ids',
									 column1='trans_id',
									 column2='pillar_id',
									 compute='_get_near_pillar'
									 )
	#near_pillar_ids=fields.function(_get_near_pillar_ids,type='many2one',obj="uis.papl.pillar",method=True,string='Near pillars id'),
	
	@api.depends('latitude','longitude')
	def _get_near_pillar(self,cr,uid,ids,context=None):
		for trans in self.browse(cr,uid,ids,context=context):
			lat1=trans.latitude
			long1=trans.longitude
			delta=0.01
			nstr=''
			max_dist=200
			pillars = self.pool.get('uis.papl.pillar').search(cr,uid,[('latitude','>',lat1-delta),('latitude','<',lat1+delta),('longitude','>',long1-delta),('longitude','<',long1+delta)],context=context)
			near_pillars=[]
			near_pillars_ids=[]
			for pid in pillars:
				pillar=self.pool.get('uis.papl.pillar').browse(cr,uid,[pid],context=context)
				if pillar:
					lat2=pillar.latitude
					long2=pillar.longitude
					dist=0
					if (lat1<>0) and (long1<>0) and (lat2<>0) and (long2<>0) and (abs(lat1-lat2)<0.1) and (abs(long1-long2)<0.1):
						rad=6372795
						#Convert to radians
						la1=lat1*math.pi/180
						la2=lat2*math.pi/180
						lo1=long1*math.pi/180
						lo2=long2*math.pi/180
						#calculate sin and cos
						cl1=math.cos(la1)
						cl2=math.cos(la2)
						sl1=math.sin(la1)
						sl2=math.sin(la2)
						delta=lo2-lo1
						cdelta=math.cos(delta)
						sdelta=math.sin(delta)
						#calculate circle len
						y = math.sqrt(math.pow(cl2*sdelta,2)+math.pow(cl1*sl2-sl1*cl2*cdelta,2))
						x = sl1*sl2+cl1*cl2*cdelta
						ad = math.atan2(y,x)
						dist = ad*rad
					print str(pillar.id)+'='+str(dist)+' deltalat='+str(lat2-lat1)+' deltalong='+str(long2-long1)
					if (dist<max_dist) and (dist>0):
						print 'Distance to'+str(pillar.id)+'='+str(dist)+' < max_dist='+str(max_dist)
						near_pillars.append(pillar)
						near_pillars_ids.append(pillar.id)
						trans.near_pillar_ids=[(4,pillar.id,0)]
						if (nstr==''):
							nstr=str(pillar.id)
						if (nstr!=''):
							nstr=nstr+','+str(pillar.id)
			#print near_pillars
			#trans.near_pillar_ids=near_pillars
			#print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
			#print trans.near_pillar_ids
			#trans.near_pillar_ids=pillar
			#trans.near_pillar_ids=(5)
			#trans.near_pillar_ids=(6,near_pillars_ids
			#trans.near_pillar_ids=[(6,0,near_pillars)]
			#print [(6,0,near_pillars_ids)]
			nstr='['+nstr+']'
			trans.str_pillar_ids=nstr
			print trans.str_pillar_ids

		'''
		
		'user_id': fields.many2one("res.users", "Users"),

_defaults = {
    'user_id': _get_users,
}
And then change the code in your method.

Try this:

def _get_users(self, cr, uid, context=None):
    users_ids = []
    officer_ids = self.search(cr, uid , 'bpl.officer', [('is_user', '=', True)])
    for record in self.browse(cr, uid, officer_ids, context=context):
        if record.user_id:
            users_ids.append(record.user_id.id)
    return users_ids
	
	
		for trans in self:
			np=[]
			pillars_obj=self.env['uis.papl.pillar']
			all_pillars_ids=pillars_obj.search([])
			print all_pillars_ids
			#all_pillars=pillars_obj.browse([])
			#browse(cr, uid, ids, context=context):
			#pillars=pillars_obj.browse(cr,uid,pillars_obj.search([]),context=context)
			#for pillar in pillars:
			#	if pillar.id<10:
			#		np.append(pillar)		
			#trans.near_pillar_ids=pillars
				'''	
			
			
