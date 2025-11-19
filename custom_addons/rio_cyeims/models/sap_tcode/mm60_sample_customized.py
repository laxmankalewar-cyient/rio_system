import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class MM60SampleCustomized(models.Model):
    _name = "mm60.sample_customized"
    _description = "MM60 Sample Customized"
    _rec_name = 'material'

    material = fields.Char('Material')
    plnt = fields.Char('Plnt')
    val_type = fields.Char('Val. Type')
    material_description = fields.Char('Material Description')
    last_chg = fields.Char('Last Chg.')
    mtyp = fields.Char('MTyp')
    matl_group = fields.Char('Matl Group')
    bun = fields.Char('BUn')
    pgr = fields.Char('PGr')
    abc = fields.Char('ABC')
    typ = fields.Char('Typ')
    valcl = fields.Char('ValCl')
    pr = fields.Char('Pr.')
    price = fields.Char('  Price')
    crcy = fields.Char('Crcy')
    empty = fields.Char(' /')
    created_by = fields.Char('Created By')




