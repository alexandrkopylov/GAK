# -*- coding: utf-8 -*-
import math, urllib, json, time, random
from openerp import models, fields, api
from PIL import Image, ImageDraw
from . import schemeAPL
from . import schemeAPL_v2
from . import uis_papl_logger
import logging
import datetime
import openerp

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

_ulog=uis_papl_logger.ulog
_logger=logging.getLogger(__name__)
_logger.setLevel(10)

#Define Passport VL constants
cv_apl_def_type=openerp._('*NT*')
cv_apl_voltage=openerp._('*0*')
cv_apl_feed=openerp._('*NFD*')
cv_apl_substation=openerp._('*NPS*')
cv_apl_voltage_abbr=openerp._('kV')
cv_apl_feed_abbr=openerp._('F')

class uis_papl_apl_cable(models.Model):
	_name='uis.papl.apl.cable'
	name=fields.Char(string="Name")
	resestivity=fields.Float(digits=(3,2), string="Resestivity")
	breaking_load=fields.Float(digits=(3,2), string="Breaking load")
	weight=fields.Float(digits=(3,2), string="Weight (kg) per km")
	diameter=fields.Float(digits=(3,2), string="Diameter (mm)")

class uis_papl_apl_pil_type(models.Model):
	_name='uis.papl.apl.pil_type'
	name=fields.Char(string="Name")
	apl_id=fields.Many2one('uis.papl.apl', string='APL')
	#apl_id_nom=fields.Integer(string="aplid")
	pillar_type_id=fields.Many2one('uis.papl.pillar.type', string="Type")
	cnt=fields.Integer(string="Pillar counts")
	numbers=fields.Char(string="Pillars numbers")

	def calc_def_apl(self,apl):
		types={}
		napt_ids=[]
		for pil in apl.pillar_id.sorted(key=lambda r:str(r.tap_id.id).zfill(3)+"_"+str(r.num_by_vl).zfill(3), reverse=False):
			tid=pil.pillar_type_id.id
			if not(tid):
				tid=0
			if not(tid in types):
				types[tid]={}
				types[tid]["cnt"]=0
				types[tid]["type"]=False
				if tid>0:
					types[tid]["type"]=pil.pillar_type_id
				types[tid]["str"]=str(pil.num_by_vl)
			else:
				types[tid]["str"]+=", "+str(pil.num_by_vl)
			if not(pil.tap_id.is_main_line):
				types[tid]["str"]+="("+str(pil.tap_id.num_by_vl)+")"
			types[tid]["cnt"] +=1
		domain=[("apl_id.id","=",apl.id)]
		for apt in self.sudo().search(domain):
			atid=apt.pillar_type_id.id
			if not(atid):
				atid=0
			if atid in types:
				napt_ids.append(apt.id)
				apt.write({
					'numbers':types[atid]["str"],
					'cnt':types[atid]["cnt"]
				})
				del types[atid]
			else:
				apt.unlink()
		for t in types:
			if not(types[t]["type"]):
				ptid=None
			else:
				ptid=types[t]["type"].id
			napt=self.sudo().create({
							  'cnt':types[t]["cnt"],
							  'numbers':types[t]["str"],
							  'pillar_type_id':ptid,
							  'apl_id':apl.id})
			napt.write({})
		return napt_ids

class uis_papl_apl_pil_materials(models.Model):
	_name='uis.papl.apl.pil_materials'
	name=fields.Char(string="Name")
	apl_id=fields.Many2one('uis.papl.apl', string='APL')
	pillar_material_id=fields.Many2one('uis.papl.pillar.material', string="Material")
	cnt=fields.Integer(string="Pillar counts")
	numbers=fields.Char(string="Pillars numbers")
	
	def calc_def_apl(self,apl):
		materials={}
		napm_ids=[]
		for pil in apl.pillar_id.sorted(key=lambda r:str(r.tap_id.id).zfill(3)+"_"+str(r.num_by_vl).zfill(3), reverse=False):
			mid=pil.pillar_material_id.id
			if not(mid):
				mid=0
			if not(mid in materials):
				materials[mid]={}
				materials[mid]["cnt"]=0
				materials[mid]["material"]=False
				if mid>0:
					materials[mid]["material"]=pil.pillar_material_id
				materials[mid]["str"]=str(pil.num_by_vl)
			else:
				materials[mid]["str"]+=", "+str(pil.num_by_vl)
			if not(pil.tap_id.is_main_line):
				materials[mid]["str"]+="("+str(pil.tap_id.num_by_vl)+")"
			materials[mid]["cnt"] +=1
		domain=[("apl_id.id","=",apl.id)]
		for apm in self.sudo().search(domain):
			amid=apm.pillar_material_id.id
			if not(amid):
				amid=0
			if amid in materials:
				napm_ids.append(apm.id)
				apm.write({
					'numbers':materials[amid]["str"],
					'cnt':materials[amid]["cnt"]
				})
				del materials[amid]
			else:
				apm.unlink()
		for m in materials:
			if not(materials[m]["material"]):
				pmid=None
			else:
				pmid=materials[m]["material"].id
			napm=self.sudo().create({
							  'cnt':materials[m]["cnt"],
							  'numbers':materials[m]["str"],
							  'pillar_material_id':pmid,
							  'apl_id':apl.id})
			napm.write({})
		return napm_ids
class uis_papl_apl_resistance(models.Model):
	_name='uis.papl.apl.resistance'
	apl_id=fields.Many2one('uis.papl.apl',string="APL")
	cable_id=fields.Many2one('uis.papl.apl.cable', string="Cable", domain="[('id','in',pos_cable_ids[0][2])])")
	pos_cable_ids=fields.Many2many('uis.papl.apl.cable',
								   relation="pos_cable_ids",
								   column1="resistance_id",
								   column2="cable_id",
								   string="Posible cables",
								   compute="_get_pos_cable_ids")
	resistivity_from_cable=fields.Boolean(string="Resistivity from cable directory")
	resestivity=fields.Float(digits=(3,2), string="Resestivity")
	resistivity_save_value=fields.Float(digits=(3,2), string="Resistivity saved value")
	total_resistance=fields.Float(digits=(3,2), string="Total resistance")
	total_resistance_save_value=fields.Float(digits=(3,2), string="Total resistance saved value")
	auto_calc_total_resistance=fields.Boolean(string="")
	_defaults={
		"apl_id": lambda self,cr,uid,c:c.get('apl_id',False)
	}
	
	@api.depends('apl_id')
	def _get_pos_cable_ids(self,cr,uid,ids,context=None):
		_logger.debug('Def pos cable_ids')
		'''tlr=_ulog(self,code='CALC_NR_PL_PL',lib=__name__,desc='Calculate near pillars for pillar')
		for pil in self.browse(cr,uid,ids,context=context):
			tlr.add_comment('[~] define new pillar for id:[%r]'%pil.id)
			lat1=pil.latitude
			long1=pil.longitude
			delta=0.01
			max_dist=300
			npillars = self.pool.get('uis.papl.pillar').search(cr,uid,[('latitude','>',lat1-delta),('latitude','<',lat1+delta),('longitude','>',long1-delta),('longitude','<',long1+delta)],context=context)
			near_pillars=[]
			near_pillars_ids=[]
			for pid in npillars:
				npil=self.pool.get('uis.papl.pillar').browse(cr,uid,[pid],context=context)
				if npil:
					if npil.id != pil.id:
						lat2=npil.latitude
						long2=npil.longitude
						dist=0
						if (lat1<>0) and (long1<>0) and (lat2<>0) and (long2<>0) and (abs(lat1-lat2)<delta) and (abs(long1-long2)<delta):
							dist=distance2points(lat1,long1,lat2,long2)
						if (dist<max_dist) and (dist>0):
							near_pillars.append(npil)
							near_pillars_ids.append(npil.id)
							pil.near_pillar_ids=[(4,npil.id,0)]
		tlr.fix_end()'''
class uis_papl_apl(models.Model):
	_name ='uis.papl.apl'
	name = fields.Char(string="Name", compute="_get_apl_name")
	short_name=fields.Char(string="Short name")
	locality=fields.Char(string="Locality")
	apl_type=fields.Char(string="Type APL")
	feeder_num=fields.Integer(string="Feeder")
	voltage=fields.Integer(string="Voltage (kV)")
	inv_num = fields.Char()
	department_id=fields.Many2one('uis.papl.department', string="Department")
	department_id_as_substation=fields.Boolean(string="As at the substation")
	department_id_save=fields.Many2one('uis.papl.department', string="Saved Department")
	bld_year =fields.Char(string="Building year")
	startexp_date = fields.Date(string="Start operations date")
	build_company = fields.Many2one('res.company',string='construction installation company')
	cable_ids=fields.Many2many('uis.papl.apl.cable',
								relation='cable_ids',
								column1='apl_id',
								column2='cable_id'
								)
	line_len=fields.Float(digits=(3,2))
	line_len_calc=fields.Float(digits=(6,2), compute='_apl_get_len')
	prol_max_len=fields.Float(digits=(2,2), compute='_apl_get_len')
	prol_med_len=fields.Float(digits=(2,2), compute='_apl_get_len')
	prol_min_len=fields.Float(digits=(2,2), compute='_apl_get_len')
	sag_max=fields.Float(digits=(3,2), string="Sag maximum")
	sag_med=fields.Float(digits=(3,2), string="Sag medium")
	sag_min=fields.Float(digits=(3,2), string="Sag minimum")
	count_circ=fields.Char(string="Number of circuits")
	climatic_conditions=fields.Char(string="Climatic conditions")
	sw_point=fields.Char(string="Switching point")
	pillar_id=fields.One2many('uis.papl.pillar','apl_id', string ="Pillars")
	apl_pil_type_ids=fields.One2many('uis.papl.apl.pil_type', 'apl_id', string="Pillar types", compute='get_pil_type_ids')
	#compute='_get_pil_type_ids',
	apl_pil_material_ids=fields.One2many('uis.papl.apl.pil_materials','apl_id', string="Pillar materials", compute='_get_pil_material_ids')
	cnt_pillar_wo_tap=fields.Integer(compute='_get_cnt_pillar_wo_tap', string="Pillars wo TAP")
	tap_ids=fields.One2many('uis.papl.tap', 'apl_id', string="Taps")
	sup_substation_id=fields.Many2one('uis.papl.substation', string="Supply substation")
	transformer_ids=fields.One2many('uis.papl.transformer','apl_id', string="Transformers")
	resistance_ids=fields.One2many('uis.papl.apl.resistance','apl_id', string="Resistance")
	tap_text=fields.Html(compute='_get_tap_text_for_apl', string="Taps")
	code_maps=fields.Text()
	status=fields.Char()
	url_maps=fields.Char(compute='_apl_get_url_maps')
	url_scheme=fields.Char(compute='_apl_get_url_scheme')  #NUPD Old use. Need delete
	image_file=fields.Char(string="Scheme File Name", compute='_get_scheme_image_file_name')
	scheme_image=fields.Binary(string="Scheme", compute='_get_scheme_image_2')
	
	#scheme_image_old=fields.Binary(string="SchemeOld", compute='_get_scheme_image')
	
	@api.one
	def get_pil_type_ids(self):
		for apl in self:
			apt_ids=self.env['uis.papl.apl.pil_type'].calc_def_apl(apl)
			apl.apl_pil_type_ids=[(6,0,apt_ids)]
			#_logger.debug(apl.apl_pil_type_ids)
			
	
	@api.one		
	def _get_pil_material_ids(self):
		for apl in self:
			apm_ids=self.env['uis.papl.apl.pil_materials'].calc_def_apl(apl)
			apl.apl_pil_material_ids=[(6,0,apm_ids)]
			
		
	def add_ml(self, cr,uid,ids,context=None):
		tlr=_ulog(self,code='ADD_NE_ML_F_APL',lib=__name__,desc='Add main line for APL)')
		re_tap=self.pool.get('uis.papl.tap').browse(cr,uid,ids,context=context)
		ntap=re_tap.create({'name':False})
		ntap.is_main_line=True
		#napl=self.pool.get('uis.papl.apl').create(cr,uid,{'name':apl_name},context=context)
		tlr.set_qnt(1)
		for apl in self.browse(cr,uid,ids,context=context):
			tlr.add_comment('[*] Add new tap (%r) to APL (%r)'%(ntap.id,apl.id))
			apl.tap_ids=[(4, ntap.id,0)]
		tlr.fix_end()
		return ntap
	
	def _get_scheme_image_2(self,cr,uid,ids,context=None):
		tlr=_ulog(self,code='CALC_APL_SCHM',lib=__name__,desc='Calculate scheme images for apl')
		i=0
		for apl in self.browse(cr,uid,ids,context=context):
			i=i+1
			tlr.add_comment('[%r] Generate image for APL id %r'%(i,apl.id))
			img = Image.new("RGBA", (schemeAPL_v2.scheme_width,schemeAPL_v2.scheme_height), (255,255,255,0))
			draw = schemeAPL_v2.drawScheme(img,apl)
			background_stream=StringIO.StringIO()
			img.save(background_stream, format="PNG")
			apl.scheme_image=background_stream.getvalue().encode('base64')
		tlr.set_qnt(i)
		tlr.fix_end()
	
	@api.onchange('department_id_as_substation')
	def _get_set_department_id(self):
		for apl in self:
			res_dep=None
			if apl.department_id_as_substation:
				apl.department_id_save=apl.department_id
				res_dep=apl.sup_substation_id.department_id
			if not(apl.department_id_as_substation):
				res_dep=apl.department_id_save
			apl.department_id=res_dep
			#apl.write({})
	
	@api.onchange('department_id')
	def _redef_as_sup_department(self):
		for apl in self:
			if apl.department_id != apl.sup_substation_id.department_id:
				apl.department_id_as_substation = False
			if apl.department_id == apl.sup_substation_id.department_id:
				apl.department_id_as_substation = True
	
	@api.onchange('sup_substation_id')
	def _redef_department_by_substation(self):
		for apl in self:
			if apl.department_id_as_substation:
				apl.department_id=apl.sup_substation_id.department_id
				
	@api.depends('short_name','apl_type','feeder_num','voltage','sup_substation_id')
	def _get_apl_name(self):
		for apl in self:
			#work with defined rpython consts
			#cv_apl_def_type - 	default type (if not defined =NT=)
			#cv_apl_voltage - 	default voltage code (if not defined = *0*)
			#cv_apl_feed	-	default code for feeder (if not defined ='*NFD*')
			#cv_apl_substation -default code for substation (if not defined ='*NPS*')
			#cv_apl_voltage_abbr	-	default abbreviation of volotage (if not defined ='kV')
			#cv_apl_feed_abbr	-	default abbreviation of feeder (if not defined ='F')

			dname=''
			def_frm='ta+"-"+va+av+" "+af+fa+"-"+sa+sn'
			#type of APL
			ta=apl.apl_type
			if not ta:
				ta=self.env.user.employee_papl_ids.code_empty_type_apl
				if not ta:
					ta=cv_apl_def_type
			#voltage of APL
			vai=apl.voltage
			va=str(vai)
			if not (vai>0):
				va=self.env.user.employee_papl_ids.code_empty_voltage_apl
				if not va:
					va=cv_apl_voltage
			#abbr voltage:
			av=self.env.user.employee_papl_ids.code_abbr_voltage_apl
			if not av:
				av=cv_apl_voltage_abbr
			
			#feed apl
			fai=apl.feeder_num
			fa=str(fai)
			if not(fai>0):
				fa=self.env.user.employee_papl_ids.code_empty_feed_apl
				if not fa:
					fa=cv_apl_feed
			#abbr feed
			af=self.env.user.employee_papl_ids.code_abbr_feed_apl
			if not af:
				af=cv_apl_feed_abbr
			#substation
			sa=apl.sup_substation_id.name
			if not sa:
				sa=self.env.user.employee_papl_ids.code_empty_substation_apl
				if not sa:
					sa=cv_apl_substation
			apl.sup_substation_id.name
			sn=''
			if apl.short_name:
				sn='('+unicode(apl.short_name)+')'
			
			if self.env.user.employee_papl_ids.disp_apl_frm:
				def_frm=self.env.user.employee_papl_ids.disp_apl_frm
			dname=eval(def_frm)
			apl.name=dname
				
	
	@api.multi
	def define_taps_num(self):
		for apl in self:
			taps=[]
			cpillar=[]
			for tap in apl.tap_ids:
				if not(tap.is_main_line):
					taps.append(tap)
					conpil=-1
					for pil in tap.pillar_ids:
						if pil.tap_id<>pil.parent_id.tap_id:
							conpil=pil.parent_id.num_by_vl
							tap.conn_pillar_id=pil.parent_id
					cpillar.append(conpil)
			sortcpillar=sorted(cpillar)
			cn_tap=1
			i=0
			for num in sortcpillar:
				i=i+1
				if num>0:
					ind=cpillar.index(num)
					cpillar[ind]=-2
					taps[ind].num_by_vl=cn_tap
					cn_tap=cn_tap+1
				
	def _get_tap_text_for_apl(self):
		for apl in self:
			hres=''
			for tap in apl.tap_ids:
				if not(tap.is_main_line):
					taplen=tap.line_len_calc;
					hres=hres+str(tap.num_by_vl)+' ('+str(tap.conn_pillar_id.num_by_vl)+') - '+str(taplen)+ '(m); <br/>'
			apl.tap_text=hres
	
	@api.depends('tap_ids','pillar_id')
	def _get_cnt_pillar_wo_tap(self):
		for apl in self:
			cnt=0
			t_pillar=0
			for pillar in apl.pillar_id:
				if not (pillar.tap_id):
					cnt=cnt+1
			apl.cnt_pillar_wo_tap=cnt
			
	
	@api.multi
	def act_show_map(self):
		tlr=_ulog(self,code='STRT_SHW_MAP_APL',lib=__name__,desc='Start show map for APL id:[%r]'%self.id)
		tlr.fix_end()
		return{
			'name': 'Maps',
			'res_model':'ir.actions.act_url',
			'type':'ir.actions.act_url',
			'target':'new',
			'url':self.url_maps,
			}
	
	@api.multi
	def act_show_scheme(self):
		print "Debug info. Start Show_map"
		print self.url_maps
		return{
			'name': 'Scheme',
			'res_model':'ir.actions.act_url',
			'type':'ir.actions.act_url',
			'target':'new',
			'url':self.url_scheme,
			#'url':'http://www.yandex.ru'
			}
	
	@api.depends('pillar_id')
	def _apl_get_url_maps(self):
		for record in self:
			record.url_maps="/apl_map/?apl_ids="+unicode(str(record.id)) #NUPD from settings
	
	@api.depends('pillar_id')
	def _apl_get_url_scheme(self):
		for record in self:
			record.url_scheme="/apl_scheme/?apl_ids="+unicode(str(record.id)) #NUPD from settings

	def _apl_get_len(self):
		for record in self:
			vsum=0
			vmin=1000
			vmax=0
			vmed=0
			vcnt=0
			for pil in record.pillar_id:
				vcnt=vcnt+1
				lpp=pil.len_prev_pillar
				if lpp>0:
					vsum=vsum+lpp
					vmed=vsum/vcnt
					if lpp<vmin:
						vmin=lpp
					if lpp>vmax:
						vmax=lpp
			record.line_len_calc=vsum
			record.prol_max_len=vmax
			record.prol_min_len=vmin
			record.prol_med_len=vmed