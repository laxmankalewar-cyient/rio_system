import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class Z7131SampleCustomized(models.Model):
    _name = "z7131.sample_customized"
    _description = "Z7131 Sample Customized"
    _rec_name = 'material'

    material = fields.Char('Material')
    material_description = fields.Char('Material Description')
    bun = fields.Char('BUn')
    matl_group = fields.Char('Matl Group')
    purchasing_text_line_01 = fields.Char('Purchasing Text Line 01')
    purchasing_text_line_02 = fields.Char('Purchasing Text Line 02')
    purchasing_text_line_03 = fields.Char('Purchasing Text Line 03')
    purchasing_text_line_04 = fields.Char('Purchasing Text Line 04')
    purchasing_text_line_05 = fields.Char('Purchasing Text Line 05')
    purchasing_text_line_06 = fields.Char('Purchasing Text Line 06')
    purchasing_text_line_07 = fields.Char('Purchasing Text Line 07')
    purchasing_text_line_08 = fields.Char('Purchasing Text Line 08')
    purchasing_text_line_09 = fields.Char('Purchasing Text Line 09')
    purchasing_text_line_10 = fields.Char('Purchasing Text Line 10')
    sect_code = fields.Char('SECT Code')
    un_spsc_code = fields.Char('UN/SPSC Code')

