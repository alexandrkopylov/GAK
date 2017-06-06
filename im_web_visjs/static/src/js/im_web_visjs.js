odoo.define('im_web_visjs.form_widgets', function (require)
{
	var core = require('web.core');
	var instance = openerp;
	imvis_time_line=instance.web.form.AbstractField.extend({
		timeline: null,
		render_value: function(){
			vals=$.parseJSON(this.get_value());
			options={};
			if (this.options){options=this.options;}
			this.$el.find('#im_time_line').remove();
			time_line_div=$('<div id="im_time_line" class="im_time_line"></div>');
			this.$el.append(time_line_div);
			this.$el.width(this.$el.parent().width());
			this.$el.height(this.$el.parent().height());
			console.log(vals);
			timeline=new vis.Timeline(time_line_div[0],vals,options);
		}
	});
	core.form_widget_registry.add('imvis_timeline', imvis_time_line);
});
