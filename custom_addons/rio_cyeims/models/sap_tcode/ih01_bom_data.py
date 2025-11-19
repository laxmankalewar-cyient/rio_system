import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class IH01BOMData(models.Model):
    _name = "ih01.bom_data"
    _description = " IH01 BOM Data"
    _rec_name = 'pu'

    navi_pu = fields.Char('Navigational FLOC')
    navi_pu_desc = fields.Char('Navigational FLOC Desc')
    pu = fields.Char('PU')
    pu_desc = fields.Char('PU Desc')
    parent_floc = fields.Char('Superior FLOC')
    parent_floc_desc = fields.Char('Superior FLOC Desc')
    floc = fields.Char('FLOC')
    floc_desc = fields.Char('FLOC Desc')
    ct = fields.Char('CT')
    ct_desc = fields.Char('CT Desc')
    pma = fields.Char('PMA')
    parent_pma = fields.Char('Parent PMA')
    pma_desc = fields.Char('PMA Description')
    material = fields.Char('Material')
    material_desc = fields.Char('Material Description')
    material_qty = fields.Char('Material Quantity')
    material_unit = fields.Char('Unit')

    site = fields.Many2one('rio.site', required=True)



