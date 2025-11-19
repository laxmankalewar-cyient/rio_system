import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class MB51SampleCustomized(models.Model):
    _name = "mb51.sample_customized"
    _description = "MB51 Sample Customized"
    _rec_name = 'material'

    material = fields.Char('Material')
    material_description = fields.Char('Material Description')
    plant = fields.Char('Plant')
    storage_location = fields.Char('Storage Location')
    movement_type = fields.Char('Movement Type')
    movement_type_text = fields.Char('Movement Type Text')
    special_stock = fields.Char('Special Stock')
    order = fields.Char('Order')
    material_document = fields.Char('Material Document')
    material_docitem = fields.Char('Material Doc.Item')
    posting_date = fields.Date('Posting Date')
    qty_in_un_of_entry = fields.Char('Qty in Un. of Entry')
    unit_of_entry = fields.Char('Unit of Entry')
    item = fields.Char('Item')
    supplier = fields.Char('Supplier')
    customer = fields.Char('Customer')


