import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class MB52SampleCustomized(models.Model):
    _name = "mb52.sample_customized"
    _description = "MB52 Sample Customized"
    _rec_name = 'plant'

    plant = fields.Char('Plant')
    name_1 = fields.Char('Name 1')
    material = fields.Char('Material')
    material_description = fields.Char('Material Description')
    base_unit_of_measure = fields.Char('Base Unit of Measure')
    unrestricted = fields.Char('Unrestricted')
    blocked = fields.Char('Blocked')
    in_quality_insp = fields.Char('In Quality Insp.')
    stock_in_transit = fields.Char('Stock in Transit')
    df_stor_loc_level = fields.Char('DF stor. loc. level')


