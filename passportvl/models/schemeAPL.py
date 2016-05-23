# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
scheme_width=800
scheme_height=400
pillar_radius=10
trans_size=20

def getSchemedata(apl_id):
    pillar_data={
        "counter":0,
        "counter_main":0,
        "pillars":[]
        }
    pillar_links={
        "counter":0,
        "links":[]
    }
    trans_data={
        "counter":0,
        "transformers":[]
    }
    apl_pillar_ids=apl_id.pillar_id
    apl_pillar_ids=apl_pillar_ids.sorted(key=lambda r:r.num_by_vl)
    if apl_pillar_ids[0]:
        pillar_data["counter"]=pillar_data["counter"]+1;
        pillar_data["pillars"].append({
                    'id':apl_pillar_ids[0].id,
                    'sid':'P'+str(apl_pillar_ids[0].id),
                    'name':apl_pillar_ids[0].name,
                    'num_by_vl':apl_pillar_ids[0].num_by_vl,
                    'start_tap_id':0,
                    'start_tap':0,
                    'y_shift':0
                })
        pp=apl_pillar_ids[0]
    tap_ids=apl_id.tap_ids
    s_tap_ids=tap_ids.sorted(key=lambda r:r.num_by_vl)
    for tap in s_tap_ids:
        print tap.name
        if tap.conn_pillar_id:
            pillar_data["counter"]=pillar_data["counter"]+1
            pillar_data["counter_main"]=pillar_data["counter_main"]+1
            pillar_data["pillars"].append({
                'id':tap.conn_pillar_id.id,
                'sid':'P'+str(tap.conn_pillar_id.id),
                'name':tap.conn_pillar_id.name,
                'num_by_vl':tap.conn_pillar_id.num_by_vl,
                'start_tap_id':tap.id,
                'start_tap':tap.num_by_vl,
                'y_shift':0
            })
            tap_pillar_ids=tap.pillar_ids
            s_tap_pillar_ids=tap_pillar_ids.sorted(key=lambda r:r.num_by_vl, reverse=True)
            if s_tap_pillar_ids[0]:
                y_shift=-1
                if (tap.num_by_vl//2)*2-tap.num_by_vl<0:
                    y_shift=1
                pillar_data["counter"]=pillar_data["counter"]+1
                pillar_data["pillars"].append({
                    'id':s_tap_pillar_ids[0].id,
                    'sid':'P'+str(s_tap_pillar_ids[0].id),
                    'name':s_tap_pillar_ids[0].name,
                    'num_by_vl':s_tap_pillar_ids[0].num_by_vl,
                    'start_tap_id':tap.id,
                    'start_tap':tap.num_by_vl,
                    'y_shift':y_shift
                })
                pillar_links["counter"]=pillar_links["counter"]+1
                pillar_links["links"].append({
                    'source_id':'P'+str(tap.conn_pillar_id.id),
                    'target_id':'P'+str(s_tap_pillar_ids[0].id)
                })
            if pp:
                pillar_links["counter"]=pillar_links["counter"]+1
                pillar_links["links"].append({
                    'source_id':'P'+str(pp.id),
                    'target_id':'P'+str(tap.conn_pillar_id.id)
                })
            pp=tap.conn_pillar_id
    apl_pillar_ids=apl_pillar_ids.sorted(key=lambda r:r.num_by_vl, reverse=True)
    if apl_pillar_ids[0]:
        pillar_data["counter"]=pillar_data["counter"]+1;
        pillar_data["pillars"].append({
                'id':apl_pillar_ids[0].id,
                'sid':'P'+str(apl_pillar_ids[0].id),
                'name':apl_pillar_ids[0].name,
                'num_by_vl':apl_pillar_ids[0].num_by_vl,
                'start_tap_id':0,
                'start_tap':pillar_data["counter_main"]+1,
                'y_shift':0
            })
    if pp:
        pillar_links["counter"]=pillar_links["counter"]+1
        pillar_links["links"].append({
            'source_id':'P'+str(pp.id),
            'target_id':'P'+str(apl_pillar_ids[0].id)
        })
    for trans in apl_id.transformer_ids:
        y_shift=-2
        if (trans.tap_id.num_by_vl//2)*2-trans.tap_id.num_by_vl<0:
            y_shift=2
        trans_data["counter"]=trans_data["counter"]+1
        trans_data["transformers"].append({
            'id':trans.id,
            'sid':'T'+str(trans.id),
            'name':trans.name,
            'tap':trans.tap_id.num_by_vl,
            'y_shift':y_shift
        })
        if trans.pillar_id:
            pillar_links["counter"]=pillar_links["counter"]+1
            pillar_links["links"].append({
                'source_id':'P'+str(trans.pillar_id.id),
                'target_id':'T'+str(trans.id)
            })
    return pillar_data, trans_data, pillar_links    

def drawpillar(draw,x,y,text):
    points=(int(x-pillar_radius/2),int(y-pillar_radius/2),int(x+pillar_radius/2),int(y+pillar_radius/2))
    draw.ellipse (points,fill="grey", outline="black")
    #fnt = ImageFont.truetype("arial.ttf", 15)
    #fnt = ImageFont.load("arial.pil")
    draw.text((int(x-pillar_radius/2),int(y-pillar_radius)), text, fill=(255,0,0,128))

def drawScheme(img,apl_id):
    points={}
    draw = ImageDraw.Draw(img)
    draw.ellipse ((90,90,110,110),fill="red", outline="blue")
    pillar_data, trans_data, pillar_links = getSchemedata(apl_id)
    dx=int(scheme_width/pillar_data["counter"])
    my=int(scheme_height/2)
    dy=int(my/3)
    for pil in pillar_data["pillars"]:
        cx=dx*pil["start_tap"]
        cy=my+pil["y_shift"]*dy
        drawpillar(draw,cx,cy,str(pil["num_by_vl"]))
        points[pil["sid"]]=(cx,cy)
    return draw