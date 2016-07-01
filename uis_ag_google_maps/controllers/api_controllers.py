# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import datetime
import json
import logging

_logger=logging.getLogger(__name__)
_logger.setLevel(10)

class maps_data_json(http.Controller):
    def _get_clean_apl_ids(self,data):
        clean_ids=[]
        for s in data['apl_ids']:
            try:
                i=int(s)
                clean_ids.append(i)
            except ValueError:
                pass
        return clean_ids
    
    def _get_apl_lines_data(self,clean_ids):
        cr, uid,context=request.cr,request.uid,request.context
        apl_obj=request.registry['uis.papl.apl']
        apl_data={
            "counter":0,
            "apls":[]
        }
        lines_data={
            "counter":0,
            "lines":[]
        }
        domain=[("id","in",clean_ids)]
        apl_ids=apl_obj.search(cr, uid, domain, context=context)
        for apl_id in apl_obj.browse(cr, uid, apl_ids, context=context):
            pil_count=0;
            apl_data["counter"]=apl_data["counter"]+1
            apl_data["apls"].append({
                    'id':apl_id.id,
                    'name':apl_id.name,
                    'type':apl_id.apl_type,
                    'feeder_num':apl_id.feeder_num,
                    'voltage':apl_id.voltage,
                    'inv_num':apl_id.inv_num,
                    'line_len':apl_id.line_len_calc,
                    'status':apl_id.status,
                    'pillar_count':"N/A", #Change to counter
                    'tap_count':"N/A" #Change to counter
                    })
            apl_id.pillar_id.sorted(key=lambda r: r.num_by_vl)
            for pillar_id in apl_id.pillar_id:
                if pillar_id.parent_id:
                    parentid=pillar_id.parent_id
                    lines_data["counter"]=lines_data["counter"]+1
                    lines_data["lines"].append({
                        'line_id':str(parentid.id)+"_"+str(pillar_id.id),
                        'lat1':pillar_id.latitude,
                        'long1':pillar_id.longitude,
                        'lat2':parentid.latitude,
                        'long2':parentid.longitude,
                        'tap_id':pillar_id.tap_id.id,
                        'apl_id':pillar_id.apl_id.id,
                        'apl_name':pillar_id.apl_id.name,
                        'tap_name':pillar_id.tap_id.name
                        
                    })
            for trans in apl_id.transformer_ids:
                if trans.pillar_id:
                    pillarid=trans.pillar_id
                    lines_data["counter"]=lines_data["counter"]+1
                    lines_data["lines"].append({
                        'line_id':str(pillarid.id)+"_T"+str(trans.id),
                        'lat1':trans.latitude,
                        'long1':trans.longitude,
                        'lat2':pillarid.latitude,
                        'long2':pillarid.longitude,
                        'tap_id':pillarid.tap_id.id,
                        'apl_id':pillarid.apl_id.id,
                        'apl_name':pillarid.apl_id.name,
                        'tap_name':pillarid.tap_id.name
                    })
        #'Return for APL %r Photo %r near Pillar %r' % (pil.apl_id.id, ph.id, pil.name)
        return apl_data,lines_data
    
    def _get_pillar_data(self,clean_ids):
        cr, uid,context=request.cr,request.uid,request.context
        #code _get_pillar_data
        apl_obj=request.registry['uis.papl.apl']
        pillar_data={
            "counter":0,
            "latitude":0,
            "longitude":0,
            "pillars":[]
        }
        minlat=120
        maxlat=0
        minlong=120
        maxlong=0
        domain=[("id","in",clean_ids)]
        apl_ids=apl_obj.search(cr, uid, domain, context=context)
        for apl_id in apl_obj.browse(cr, uid, apl_ids, context=context):
            apl_id.pillar_id.sorted(key=lambda r: r.num_by_vl)
            for pillar_id in apl_id.pillar_id:
                #print "Do pillar"+pillar_id.name
                pillar_data["counter"]=pillar_data["counter"]+1
                if pillar_id.latitude>maxlat:
                    maxlat=pillar_id.latitude
                if pillar_id.latitude<minlat:
                    minlat=pillar_id.latitude
                if pillar_id.longitude>maxlong:
                    maxlong=pillar_id.longitude
                if pillar_id.longitude<minlong:
                    minlong=pillar_id.longitude
                pillar_data["pillars"].append({
                    'id':pillar_id.id,
                    'name':pillar_id.name,
                    'apl':apl_id.name,
                    'apl_id':apl_id.id,
                    'tap_id':pillar_id.tap_id.id,
                    'elevation':pillar_id.elevation,
                    'latitude': escape(str(pillar_id.latitude)),
                    'longitude': escape(str(pillar_id.longitude)),
                    'num_by_vl':pillar_id.num_by_vl,
                    'prev_id':pillar_id.parent_id.id,
                    'type_id':pillar_id.pillar_type_id.id,
                    'rotation':0,  #Add direction pillar
                    'state':'EXPLOTATION' #Add state from MRO
                    #'prevlatitude': escape(str(pillar_id.prev_latitude)),
                    #'prevlangitude': escape(str(pillar_id.prev_longitude))
                    })
        medlat=(maxlat+minlat)/2
        medlong=(maxlong+minlong)/2
        pillar_data["latitude"]=medlat
        pillar_data["longitude"]=medlong
        pillar_data["minlat"]=minlat
        pillar_data["maxlat"]=maxlat
        pillar_data["minlong"]=minlong
        pillar_data["maxlong"]=maxlong
        #end code _pillar_data
        return pillar_data
    
    def _get_trans_data(self,clean_ids):
        cr, uid,context=request.cr,request.uid,request.context
        trans_data={
            "counter":0,
            "trans":[]
        }
        apl_obj=request.registry['uis.papl.apl']
        domain=[("id","in",clean_ids)]
        apl_ids=apl_obj.search(cr,uid,domain,context=context)
        for apl in apl_obj.browse(cr,uid,apl_ids, context=context):
            for trans in apl.transformer_ids:
                trans_data["counter"]=trans_data["counter"]+1
                trans_data["trans"].append({
                    'id':trans.id,
                    'name':trans.name,
                    'state':trans.state,
                    'longitude':trans.longitude,
                    'latitude':trans.latitude
                })
        return trans_data
    
    #Define API hash functions
    @http.route('/apiv1/apl/data/hash',type='json', auth="public", csfr=False)
    def api_v1_apl_data_hash(self, *arg, **post):
        start=datetime.datetime.now()
        #cr,uid,context=request.cr, request.uid, request.context
        data=json.loads(json.dumps(request.jsonrequest))
        clean_ids=self._get_clean_apl_ids(data)
        apl_data,lines_data=self._get_apl_lines_data(clean_ids)
        out=hash(str(apl_data)+str(lines_data))
        values ={
            'hash_apl':json.dumps(out)
        }
        stop=datetime.datetime.now()
        elapsed=stop-start
        _logger.info('Generate APL data HASH in %r seconds'%elapsed.total_seconds())
        return values
    
    @http.route('/apiv1/pillar/data/hash', type='json', auth="public", csfr=False)
    def api_v1_pillar_data_hash(self, *arg, **post):
        start=datetime.datetime.now()
        #cr,uid,context=request.cr, request.uid, request.context
        data=json.loads(json.dumps(request.jsonrequest))
        clean_ids=self._get_clean_apl_ids(data)
        pillar_data=self._get_pillar_data(clean_ids)
        out=hash(str(pillar_data))
        values ={
            'hash_pillar':json.dumps(out)
        }
        stop=datetime.datetime.now()
        elapsed=stop-start
        _logger.info('Generate PILLAR data HASH in %r seconds'%elapsed.total_seconds())
        return values
    
    @http.route('/apiv1/trans/data/hash',type='json', auth="public", csfr=False)
    def api_v1_trans_data_hash(self, *arg, **post):
        start=datetime.datetime.now()
        data=json.loads(json.dumps(request.jsonrequest))
        clean_ids=self._get_clean_apl_ids(data)
        trans_data=self._get_trans_data(clean_ids)
        out=hash(str(trans_data))
        values ={
            'hash_trans':json.dumps(out)
        }
        stop=datetime.datetime.now()
        elapsed=stop-start
        _logger.info('Generate TRANS data HASH in %r seconds'%elapsed.total_seconds())
        return values
    
    #Define Data functions
    @http.route('/apiv1/apl/data',type="json", auth="public", csfr=False)
    def api_v1_apl_data(self, *arg, **post):
        start=datetime.datetime.now()
        data=json.loads(json.dumps(request.jsonrequest))
        clean_ids=self._get_clean_apl_ids(data)
        apl_data,lines_data=self._get_apl_lines_data(clean_ids)
        values ={
            'apl_data':json.dumps(apl_data),
            'lines_data':json.dumps(lines_data)
        }
        stop=datetime.datetime.now()
        elapsed=stop-start
        _logger.info('Generate APL data in %r seconds'%elapsed.total_seconds())
        return values
    
    @http.route('/apiv1/pillar/data', type="json", auth="public", csfr=False)
    def api_v1_pillar_data(self, *arg, **post):
        start=datetime.datetime.now()
        #cr, uid, context=request.cr, request.uid, request.context
        data=json.loads(json.dumps(request.jsonrequest))
        clean_ids=self._get_clean_apl_ids(data)
        pillar_data=self._get_pillar_data(clean_ids)
        values ={
            'pillar_data':json.dumps(pillar_data)
        }
        stop=datetime.datetime.now()
        elapsed=stop-start
        _logger.info('Generate PILLAR data in %r seconds'%elapsed.total_seconds())
        return values
    
    @http.route('/apiv1/trans/data', type="json", auth="public", csfr=False)
    def api_v1_trans_data(self, *arg, **post):
        start=datetime.datetime.now()
        #cr, uid, context=request.cr, request.uid, request.context
        #trans_obj =request.registry['uis.papl.transmormer']
        data=json.loads(json.dumps(request.jsonrequest))
        clean_ids=self._get_clean_apl_ids(data)
        trans_data=self._get_trans_data(clean_ids)
        values ={
            'trans_data':json.dumps(trans_data)
        }
        stop=datetime.datetime.now()
        elapsed=stop-start
        _logger.info('Generate TRANS data in %r seconds'%elapsed.total_seconds())
        return values
    
    #Define Newcoord data
    @http.route('/apiv1/pillar/newcoorddrop', type="json", auth="public", csfr=False)
    def api_v1_pillar_new_coordinate_drop(self, *arg, **post):
        _logger.info('POST Newcoord json data for pillar (PILLAR)')
        cr, uid, context=request.cr, request.uid, request.context
        pillar_obj = request.registry['uis.papl.pillar']
        data=json.loads(json.dumps(request.jsonrequest))
        pid=data['pillar_id']
        new_latitude=data['new_latitude']
        new_longitude=data['new_longitude']
        domain=[("id","in",[pid])]
        pillar_ids=pillar_obj.search(cr, uid, domain, context=context)
        for pil in pillar_obj.browse(cr, uid, pillar_ids, context=context):
            pil.latitude=new_latitude
            pil.longitude=new_longitude
        values ={
            'result':1
        }
        return values
    @http.route('/apiv1/trans/newcoorddrop', type="json", auth="public", csfr=False)
    def api_v1_trans_new_coordinate_drop(self, *arg, **post):
        _logger.info('POST Newcoord json data for transformator (TRANS)')
        cr, uid, context=request.cr, request.uid, request.context
        trans_obj = request.registry['uis.papl.transformer']
        data=json.loads(json.dumps(request.jsonrequest))
        pid=data['trans_id']
        new_latitude=data['new_latitude']
        new_longitude=data['new_longitude']
        domain=[("id","in",[pid])]
        trans_ids=trans_obj.search(cr, uid, domain, context=context)
        for trans in trans_obj.browse(cr, uid, trans_ids, context=context):
            trans.latitude=new_latitude
            trans.longitude=new_longitude
        values ={
            'result':1
        }
        return values
    