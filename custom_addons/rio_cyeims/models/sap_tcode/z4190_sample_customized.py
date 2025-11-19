import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class Z4190SampleCustomized(models.Model):
    _name = "z4190.sample_customized"
    _description = "Z4190 Sample Customized"
    _rec_name = 'plant'

    plant = fields.Char('Plant')
    group = fields.Char('Group')
    grpcountr = fields.Char('Grp.Countr')
    short_text = fields.Char('Short Text')
    plannergrp = fields.Char('PlannerGrp')
    planner_group = fields.Char('Planner Group')
    activity = fields.Char('Activity')
    ctrl_key = fields.Char('Ctrl Key')
    operation_short_text = fields.Char('Operation Short Text')
    component = fields.Char('Component')
    material_description = fields.Char('Material Description')
    item_cat = fields.Char('Item Cat.')
    status = fields.Char('Status')
    usage = fields.Char('Usage')
    assembly = fields.Char('Assembly')
    functional_location = fields.Char('Functional Location')
    pu_label = fields.Char('PU label')
    quantity = fields.Char('Quantity')
    comp_unit = fields.Char('Comp unit')
    valid_from = fields.Date('Tasklist Header Valid From')
    valid_from_1 = fields.Date('Alloc of BOM to Operations Valid From')
    valid_from_2 = fields.Date('Operation Valid From')
    valid_from_3 = fields.Date('BOM Item Valid From')





