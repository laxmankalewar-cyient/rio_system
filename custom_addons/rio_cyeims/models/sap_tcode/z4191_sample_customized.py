import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class Z4191SampleCustomized(models.Model):
    _name = "z4191.sample_customized"
    _description = "Z4191 Sample Customized"
    _rec_name = 'plant'

    plant = fields.Char('Plant')
    pu_label = fields.Char('PU label')
    functional_location = fields.Char('Functional Location')
    functional_loc_desc = fields.Char('Functional Loc Desc')
    material_pathway = fields.Char('Material Pathway')
    assembly = fields.Char('Assembly')
    material = fields.Char('Material')
    material_description = fields.Char('Material Description')
    matl_group = fields.Char('Matl Group')
    matlstatus = fields.Char('MatlStatus')
    val_cat = fields.Char('Val. Cat.')
    spl_ind = fields.Char('Spl Ind')
    equipment = fields.Char('Equipment')
    bom_quanty = fields.Char('BOM Quanty')






