from odoo import api, fields, models, _, tools

import logging

_logger = logging.getLogger(__name__)


class IH06FlocsData(models.Model):
    _name = "ih06.floc_data"
    _description = 'IH06 Floc Data'
    _rec_name = 'pu'

    pu = fields.Char("PU")
    floc = fields.Char("Floc")
    floc_desc = fields.Char("Floc Desc")
    site_code = fields.Char("Site Code")
    parent_floc = fields.Char("Superior functional location")
    construction = fields.Char("Construction type")
    constr_desc = fields.Char("Construction Desc")
