import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class Z7134SampleCustomized(models.Model):
    _name = "z7134.sample_customized"
    _description = "Z7134 Sample Customized"
    _rec_name = 'riomatno'

    riomatno = fields.Char('RioMatNo.')
    riomatdesc = fields.Char('RioMatDesc')
    int_no = fields.Char('Int. no.')
    internal_material_description = fields.Char('Internal Material Description')
    mpn = fields.Char('MPN')
    mfr = fields.Char('Mfr')
    matlstatus = fields.Char('MatlStatus')
    statdesc = fields.Char('StatDesc')



