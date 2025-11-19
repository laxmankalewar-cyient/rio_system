import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class ME2MSampleCustomized(models.Model):
    _name = "me2m.sample_customized"
    _description = "ME2M Sample Customized"
    _rec_name = 'purchasing_document'

    purchasing_doc_type = fields.Char('Purchasing Doc. Type')
    purchasing_document = fields.Char('Purchasing Document')
    item = fields.Char('Item')
    material = fields.Char('Material')
    short_text = fields.Char('Short Text')
    purchasing_group = fields.Char('Purchasing Group')
    po_history_release_documentation = fields.Char('PO history/release documentation')
    vendor_supplying_plant = fields.Char('Vendor/supplying plant')
    plant = fields.Char('Plant')
    storage_location = fields.Char('Storage Location')
    quantity_in_sku = fields.Char('Quantity in SKU')
    stockkeeping_unit = fields.Char('Stockkeeping unit')
    net_price = fields.Char('Net price')
    currency = fields.Char('Currency')
    price_unit = fields.Char('Price Unit')
    still_to_be_delivered = fields.Char('Still to be delivered (qty)')



