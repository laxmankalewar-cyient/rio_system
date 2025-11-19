import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class SpareFinderSampleCustomized(models.Model):
    _name = "spare.finder_customized"
    _description = "Spare Finder Sample Customized"
    _rec_name = 'sphera'

    sphera = fields.Char('Sphera #')
    erp_instance = fields.Char('ERP Instance')
    material = fields.Char('Material')
    short_description = fields.Char('Short Description')
    long_description = fields.Char('Long Description')
    manufacturer = fields.Char('Manufacturer')
    part_number = fields.Char('Part Number')
    base_uom = fields.Char('Base UOM')
    un_spsc_code = fields.Char('UN/SPSC Code')





