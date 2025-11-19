import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class Z7116SampleCustomized(models.Model):
    _name = "z7116.sample_customized"
    _description = "Z7116 Sample Customized"
    _rec_name = 'material'

    traffic_light = fields.Char('Traffic Light')
    plant = fields.Char('Plant')
    valuation_category = fields.Char('Valuation Category')
    description = fields.Char('Description')
    material = fields.Char('Material')
    material_description = fields.Char('Material Description')
    material_type = fields.Char('Material Type')
    stock_on_hand_consignment = fields.Char('Stock on Hand excluding VMI/Consignment')
    vmi_consignment = fields.Char('VMI/Consignment')
    mrp_cont = fields.Char('MRP Cont.')
    mrp_type = fields.Char('MRP Type')
    lot_size = fields.Char('Lot size')
    unsrv = fields.Char('Unsrv')
    res_req_release = fields.Char('Res. Req. Release')
    rel_reservations = fields.Char('Rel. Reservations')
    ltime = fields.Char('Ltime')
    usg_3_mts = fields.Char('Usg 3 Mts')
    usg_12_mts = fields.Char('Usg 12 Mts')
    reorder = fields.Char('Reorder')
    max_stk_le = fields.Char('Max stk le')
    refurbishment_order_exists = fields.Char('Refurbishment Order Exists')
    total_value = fields.Char('Total Value')

