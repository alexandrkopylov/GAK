# -*- coding: utf-8 -*-

import math, urllib, json, time
import os, exifread
import re
from PIL import Image
import base64
import psycopg2
from openerp import models, fields, api, tools
from datetime import datetime

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

def distance2points(lat1,long1,lat2,long2):
	dist=0
	if (lat1<>0) and (long1<>0) and (lat2<>0) and (long2<>0):
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
	return dist

def dms2dd(degrees,minutes,seconds, direction):
	dd=float(degrees)+float(minutes)/60+float(seconds)/(60*60)
	if direction == 'S' or direction =='W':
		dd *=-1
	return dd

def parse_dms(dms,direction):
	parts=re.split('[^\d\w]+',dms)
	dd=dms2dd(parts[1],parts[2],int(parts[3])/int(parts[4]),direction)
	print parts
	return dd

def parse_date(str_date):
	parts=re.findall(r"[\d']+", str_date)
	rdate= datetime.strptime(str(str_date),'%Y:%m:%d %H:%M:%S')
	return rdate

def strdiv(strdiv):
	print strdiv
	parts=re.findall(r"[\d']+",str(strdiv))
	print parts
	rval=int(parts[0])/int(parts[1])
	return rval
	
class uis_ap_photo(models.Model):
	_name='uis.ap.photo'
	_description='Photo_apl'
	name=fields.Char('Name')
	image=fields.Binary(string='Image')
	image_length=fields.Integer(string='Image Length')
	image_width=fields.Integer(string='Image Width')
	image_800=fields.Binary(string='Image800', compute='_get_800_img')
	focal_length=fields.Float(digits=(2,4), string="Focal Length")
	thumbnail=fields.Binary(string="Thumbnail")
	image_filename=fields.Char(string='Image file name')
	image_date=fields.Datetime(string='Image date')
	load_hist_id=fields.One2many('uis.ap.photo.load_hist','photo_ids','Load data')
	longitude=fields.Float(digits=(2,6), string='Longitude')
	latitude=fields.Float(digits=(2,6), string='Latitude')
	altitude=fields.Float(digits=(2,4), string='Altitude')
	near_pillar_ids=fields.Many2many('uis.papl.pillar',
									 relation='photo_near_pillar',
									 column1='photo_id',
									 column2='pillar_id',
									 compute='_get_near_photo_pillar'
									 )
	near_apl_ids=fields.Many2many('uis.papl.apl',
							 relation='photo_near_apl',
							 column1='photo_id',
							 column2='apl_id',
							 compute='_get_near_photo_apl')
	near_transformer_ids=fields.Many2many('uis.papl.transformer',
										  relation='photo_near_trans',
										  column1='photo_id',
										  column2='transformer_id',
										  compute='_get_near_trans_ids')
	
	def _get_800_img(self,cr,uid,ids,context=None):
		for photo in self.browse(cr,uid,ids,context=context):
			#image_stream=StringIO.StringIO(photo.image.decode('base64'))
			#image=Image.open(image_stream)
			awi=int(photo.image_width/2)
			ahe=int(photo.image_length/2)
			#size=awi,ahe
			#if image.size != size:
			#	image.thumbnail(size, Image.ANTIALIAS)
			#	sharpener=ImageEnhance.Sharpness(image.convert('RGBA'))
				
			#photo.image_800=tools.image_resize_image(photo.image, size=(int(photo.image_length/2),int(photo.image_width/2)), encoding='base64')
		
	@api.depends('latitude', 'longitude')
	def _get_near_trans_ids(self,cr,uid,ids,context=None):
		for photo in self.browse(cr,uid,ids,context=context):
			lat1=photo.latitude
			long1=photo.longitude
			delta=0.01
			nstr=''
			max_dist=50
			trans = self.pool.get('uis.papl.transformer').search(cr,uid,[('latitude','>',lat1-delta),('latitude','<',lat1+delta),('longitude','>',long1-delta),('longitude','<',long1+delta)],context=context)
			near_pillars=[]
			near_pillars_ids=[]
			for tr in trans:
				transformer=self.pool.get('uis.papl.transformer').browse(cr,uid,[tr],context=context)
				if transformer:
					lat2=transformer.latitude
					long2=transformer.longitude
					dist=0
					if (lat1<>0) and (long1<>0) and (lat2<>0) and (long2<>0) and (abs(lat1-lat2)<0.1) and (abs(long1-long2)<0.1):
						dist=distance2points(lat1,long1,lat2,long2)
					if (dist<max_dist) and (dist>0):
						photo.near_transformer_ids=[(4,transformer.id,0)]
		
	@api.depends('near_pillar_ids')
	def _get_near_photo_apl(self,cr,uid,ids,context=None):
		for photo in self.browse(cr,uid,ids,context=context):
			apl_ids=[]
			for pil in photo.near_pillar_ids:
				print pil.name
				print pil.apl_id.id
				if pil.apl_id not in apl_ids:
					apl_ids.append(pil.apl_id.id)
					photo.near_apl_ids=[(4,pil.apl_id.id,0)]
			
	@api.depends('latitude','longitude')
	def _get_near_photo_pillar(self,cr,uid,ids,context=None):
		for photo in self.browse(cr,uid,ids,context=context):
			lat1=photo.latitude
			long1=photo.longitude
			delta=0.01
			nstr=''
			max_dist=50
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
						dist=distance2points(lat1,long1,lat2,long2)
					if (dist<max_dist) and (dist>0):
						near_pillars.append(pillar)
						near_pillars_ids.append(pillar.id)
						photo.near_pillar_ids=[(4,pillar.id,0)]
						#if (nstr==''):
						#	nstr=str(pillar.id)
						#if (nstr!=''):
						#	nstr=nstr+','+str(pillar.id)
						#	print str(pillar.id)+':'+nstr
			
class uis_ap_photo_load_hist(models.Model):
	_name='uis.ap.photo.load_hist'
	_description='Photo_apl_hist'
	name=fields.Char('Name')
	load_date=fields.Date(string='Load date')
	photo_count=fields.Integer(string='Photo_count')
	photo_ids=fields.Many2one('uis.ap.photo', string='Photos')
	folder_name=fields.Char(string='Folder')
	
	def load_photos(self, cr,uid,ids,context=None):
		re_photos=self.pool.get('uis.ap.photo').browse(cr,uid,ids,context=context)
		print "Start load photos"
		path='/home'
		val=self.browse(cr,uid,ids,context=context)
		if val.folder_name != '':
			path=val.folder_name
		for filen in os.listdir(path):
			if filen.endswith(".JPG"):
				img=file(path+'/'+filen,'rb').read().encode('base64')
				with open(path+'/'+filen,'rb') as f:
					print (filen)
					tags=exifread.process_file(f)
					dms_longitude=tags["GPS GPSLongitude"]
					dms_longitude_ref=tags["GPS GPSLongitudeRef"]
					plong=parse_dms(str(dms_longitude),dms_longitude_ref)
					dms_latitude=tags["GPS GPSLatitude"]
					dms_latitude_ref=tags["GPS GPSLatitudeRef"]
					plat=parse_dms(str(dms_latitude),dms_latitude_ref)
					idate=tags["Image DateTime"]
					
					#EXIF ExifImageWidth, value 4000
					ciw=str(tags["EXIF ExifImageWidth"])
					#EXIF ExifImageLength, value 3000
					cil=str(tags["EXIF ExifImageLength"])
					#EXIF FocalLength, value 361/100
					cfl=strdiv(tags["EXIF FocalLength"])
					#GPS GPSAltitude, value 181921/1000
					calt=strdiv(tags["GPS GPSAltitude"])

					print plat,plong
					for tag in tags.keys():
						if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
							print "Key: %s, value %s" % (tag, tags[tag])
					idate=parse_date(str(idate))
					# !!!! Need validate name file
					np=re_photos.create({'name':str(idate.year)+'_'+str(idate.month)+'_'+str(idate.day)+'_'+str(filen)})
					np.latitude=plat
					np.longitude=plong
					np.image_filename=filen
					np.image=img
					np.image_date=idate
					np.image_length=int(cil)
					np.image_width=int(ciw)
					np.focal_length=cfl
					np.altitude=calt
					#np.load_hist_id=val.id
					#np.image_date.from_string(idate)
					np.thumbnail=base64.b64encode(tags['JPEGThumbnail'])
				