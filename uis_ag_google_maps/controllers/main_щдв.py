# -*- coding: utf-8 -*-

#import json
#from openerp import SUPERUSER_ID
#rom openerp.addons.web import http
#from openerp.addons.web.http import request
#from openerp.tools import html_escape as escape

from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

print "Create Pillar Google Maps Class"
class pillar_google_map(http.Controller):
    '''
    This class generates on-the-fly partner maps that can be reused in every
    website page. To do so, just use an ``<iframe ...>`` whose ``src``
    attribute points to ``/google_map`` (this controller generates a complete
    HTML5 page).

    URL query parameters:
    - ``partner_ids``: a comma-separated list of ids (partners to be shown)
    - ``partner_url``: the base-url to display the partner
        (eg: if ``partner_url`` is ``/partners/``, when the user will click on
        a partner on the map, it will be redirected to <myodoo>.com/partners/<id>)

    In order to resize the map, simply resize the ``iframe`` with CSS
    directives ``width`` and ``height``.
    '''
    @http.route('/sp', auth='public')
    def save_new_point(self, *arg, **post):
        print 'Getting /sp'
        cr,uid,context=request.cr,request.uid, request.context
        pillar_obj=request.registry['uis.papl.pillar']
        g_pillar_id=post.get('id',"")
        g_pillar_lat=post.get('nltd',"")
        g_pillar_lng=post.get('nlng',"")
        domain=[("id","=",g_pillar_id)]
        pillar_id=pillar_obj.search(cr,uid,domain, context=context)
        print pillar_id
        for record in pillar_obj.browse(cr, uid, pillar_id, context=context):
            print record.name
            record.latitude=g_pillar_lat
            record.longitude=g_pillar_lng
        
        
    @http.route('/apl_map', auth='public')
    def apl_map(self, *arg, **post):
        print "Start Create maps"
        cr, uid, context = request.cr, request.uid, request.context
        pillar_obj = request.registry['uis.papl.pillar']
        apl_obj=request.registry['uis.papl.apl']
        values=""
        clean_ids=[]
        for s in post.get('apl_ids',"").split(","):
            try:
                i=int(s)
                clean_ids.append(i)
                print i
            except ValueError:
                pass
        domain=[("id","in",clean_ids)]
        apl_ids=apl_obj.search(cr, uid, domain, context=context)
        #apl_ids=apl_obj.search(cr, SUPERUSER_ID, domain, context=context)
        pillar_data={
            "counter":0,
            "latitude":0,
            "longitude":0,
            "pillars":[]
        }
        s_data={
            "counter":0
        }
        minlat=120
        maxlat=0
        minlong=120
        maxlong=0
        for apl_id in apl_obj.browse(cr, uid, apl_ids, context=context):
            print apl_id.name
            apl_id.pillar_id.sorted(key=lambda r: r.num_by_vl)
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            for pillar_id in apl_id.pillar_id:
                print "Do pillar"+pillar_id.name
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
                    'latitude': escape(str(pillar_id.latitude)),
                    'longitude': escape(str(pillar_id.longitude)),
                    #'prevlatitude': escape(str(pillar_id.prev_latitude)),
                    #'prevlangitude': escape(str(pillar_id.prev_longitude))
                    })
        medlat=(maxlat+minlat)/2
        medlong=(maxlong+minlong)/2
        pillar_data["latitude"]=medlat
        pillar_data["longitude"]=medlong
        values = {
            #'partner_url': post.get('partner_url'),
            'pillar_data': json.dumps(pillar_data)
        }
        return request.render("uis_ag_google_maps.uis_google_map", values)
'''

        # search for partners that can be displayed on a map
        domain = [("id", "in", clean_ids), ('website_published', '=', True), ('is_company', '=', True)]
        partners_ids = partner_obj.search(cr, SUPERUSER_ID, domain, context=context)

        # browse and format data
        partner_data = {
        "counter": len(partners_ids),
        "partners": []
        }
        request.context.update({'show_address': True})
        for partner in partner_obj.browse(cr, SUPERUSER_ID, partners_ids, context=context):
            # TODO in master, do not use `escape` but `t-esc` in the qweb template.
            partner_data["partners"].append({
                'id': partner.id,
                'name': escape(partner.name),
                'address': escape('\n'.join(partner.name_get()[0][1].split('\n')[1:])),
                'latitude': escape(str(partner.partner_latitude)),
                'longitude': escape(str(partner.partner_longitude)),
                })

        # generate the map
        values = {
            'partner_url': post.get('partner_url'),
            'partner_data': json.dumps(partner_data)
        }
        return request.website.render("website_google_map.google_map", values)
'''