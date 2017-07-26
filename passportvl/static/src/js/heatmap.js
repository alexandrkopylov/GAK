odoo.define('passportvl.form_widgets', function (require)
{
    var core = require('web.core');
	var AplMAP=core.form_widget_registry.get('aplmap');
	/*var Model=require('web.Model');*/
	var instance = openerp;
	
	heatmap=instance.web.form.AbstractField.extend(
    {
        hmap: null,
		c_radius:10,

		render_value: function()
		{
			if (this.options.radius>0){
				c_radius=this.options.radius;
			}
			this.$el.find('#heat_def_map').remove();
            var def_heat_map=$('<div id="heat_def_map" class="heat_map"></div>');
            /*def_heat_map.css('width','100%');
			#def_heat_map.css('height','100%');*/
			this.$el.append(def_heat_map);
			data = new ol.source.Vector();
			var OsmLayer=new ol.layer.Tile({source: new ol.source.OSM()});
			
			cwm=this.$el;
			hmap=new ol.Map({
				controls:[new ol.control.FullScreen()],
				target:def_heat_map.get()[0],
				renderer: 'canvas',
				layers: [OsmLayer]});
			
			this.$el.width(this.$el.parent().width());
			this.$el.height(this.$el.parent().height());
			hmap.setSize([def_heat_map.parent().width(),def_heat_map.parent().height()]);
            this.hmap=hmap;
				
			a_val=$.parseJSON(this.get_value());
			sumlat=0;
			sumlng=0;
			cnt=a_val.length;
			a_val.forEach(function(item,i,a_val){
				var coord=[item.lng,item.lat];
				
				sumlat=sumlat+item.lat;
				sumlng=sumlng+item.lng;
				var lonLat = new ol.geom.Point(ol.proj.transform(coord, 'EPSG:4326', 'EPSG:3857'));
				var pointFeature=new ol.Feature({
					geometry:lonLat,
					weight:item.cnt
				});
				data.addFeature(pointFeature);
			
			hmap.setView(new ol.View({
                center: ol.proj.transform([sumlng/cnt, sumlat/cnt], 'EPSG:4326', 'EPSG:3857'),
                zoom: 13
				}));	
			});
			heatMapLayer = new ol.layer.Heatmap({
				source: data,
				radius: 3
			});
			hmap.addLayer(heatMapLayer);
		}
	});
	
	defectheatmap=AplMAP.extend(
	{
		c_radius:10,
		
		GetAplID: function()
		{
			return this.field_manager.get_field_value("id");
		},
		render_value: function()
		{
			this._super.apply(this, arguments);
		},
		LoadAllObjects: function()
		{
			this._super.apply(this, arguments);
			var hmap=this.map;
			
			data = new ol.source.Vector();
			var OsmLayer=new ol.layer.Tile({source: new ol.source.OSM()});
				
			a_val=$.parseJSON(this.get_value());
			sumlat=0;
			sumlng=0;
			cnt=a_val.length;
			a_val.forEach(function(item,i,a_val){
				var coord=[item.lng,item.lat];
				
				sumlat=sumlat+item.lat;
				sumlng=sumlng+item.lng;
				var lonLat = new ol.geom.Point(ol.proj.transform(coord, 'EPSG:4326', 'EPSG:3857'));
				var pointFeature=new ol.Feature({
					geometry:lonLat,
					weight:item.cnt
				});
				data.addFeature(pointFeature);
			
			hmap.setView(new ol.View({
                center: ol.proj.transform([sumlng/cnt, sumlat/cnt], 'EPSG:4326', 'EPSG:3857'),
                zoom: 12
				}));	
			});
			heatMapLayer = new ol.layer.Heatmap({
				source: data,
				radius: 3,
				blur: 5,
			});
			hmap.addLayer(heatMapLayer);
		},
	});
	
	core.form_widget_registry.add('heatmap', heatmap);
	core.form_widget_registry.add('defectheatmap', defectheatmap)
});