import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class Z5001SampleCustomized(models.Model):
    _name = "z5001.sample_customized"
    _description = "Z5001 Sample Customized"
    _rec_name = 'material'

    material = fields.Char('Material')
    material_description = fields.Char('Material Description')
    inventory = fields.Char('Inventory')
    base_unit_of_measure = fields.Char('Base Unit of Measure')
    safety_stock = fields.Char('Safety Stock')
    minimum_stock = fields.Char('Minimum Stock')
    minimum_inventory = fields.Char('Minimum Inventory')
    maximum_stock = fields.Char('Maximum Stock')
    maximum_inventory = fields.Char('Maximum Inventory')
    traffic_light = fields.Char('Traffic Light')
