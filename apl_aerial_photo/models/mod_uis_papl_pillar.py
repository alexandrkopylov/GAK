# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
import logging

_logger=logging.getLogger(__name__)
_logger.setLevel(10)

class uis_papl_photo_mod_uis_papl_pillar(models.Model):
	_inherit = 'uis.papl.pillar'
	_name = 'uis.papl.pillar'
	photo_count=fields.Integer(string="Photo count", compute='_get_photo_count')
	photo_ids=fields.Many2many(string="Photos", comodel_name="uis.ap.photo", relation="photo_pillar_rel", column1="pillar_id", column2="photo_id")
	
	def _get_photo_count(self):
		for pillar in self:
			pillar.photo_count=len(pillar.photo_ids)+1
