import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class IW38SampleCustomized(models.Model):
    _name = "iw38.sample_customized"
    _description = " IW38 Sample Customized"
    _rec_name = 'order_type'

    order_type = fields.Char('Order Type')
    notification = fields.Char('Notification')
    order = fields.Char('Order')
    bas_start_date = fields.Date('Bas. start date')
    stat_flag = fields.Char('Stat. Flag')
    functional_loc = fields.Char('Functional Loc.')
    funclocdesc = fields.Char('FuncLocDesc')
    description = fields.Char('Description')
    system_status = fields.Char('System status')
    user_status = fields.Char('User status')
    main_workctr = fields.Char('Main WorkCtr')
    planner_group = fields.Char('Planner group')
    created_on = fields.Date('Created on')
    po_number = fields.Char('PO number')
    plant = fields.Char('Plant')
    material = fields.Char('Material')
    group = fields.Char('Group')
    group_counter = fields.Char('Group Counter')
    basic_fin_date = fields.Date('Basic fin. date')

