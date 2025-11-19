import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class UNSPSCCode(models.Model):
    _name = "unspsc.code"
    _description = "UNSPSC Code"
    _rec_name = 'commodity_desc'

    segment = fields.Char('Segment')
    segment_desc = fields.Char('Segment Desc')
    family = fields.Char('Family')
    family_desc = fields.Char('Family Desc')
    class_1 = fields.Char('Class')
    class_desc = fields.Char('Class Desc')
    commodity = fields.Char('Commodity')
    commodity_desc = fields.Char('Commodity Desc')

    def name_get(self):
        return [(record.id, f"({record.commodity}) - {record.commodity_desc}") for record in self]
