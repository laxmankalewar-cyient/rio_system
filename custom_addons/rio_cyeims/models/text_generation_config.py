import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class TextGenerationFields(models.Model):
    _name = "text.generation_fields"
    _description = "Text Fields"
    _rec_name = 'text_field'
    _order = "sequence"

    text_field = fields.Many2one('ir.model.fields', string="Text Field")
    ttype = fields.Selection(related='text_field.ttype')
    sequence = fields.Integer(string="sequence", required=True)
    text_prefix = fields.Char("Prefix Text")
    model_id = fields.Many2one('text.generation_config', 'Model ID', readonly=True)
    field_description = fields.Char(related='text_field.field_description')
    data_source = fields.Many2one(related='model_id.related_model')


class TextGenerationConfig(models.Model):
    _name = "text.generation_config"
    _description = "Text Generation Config"
    _rec_name = 'name'

    name = fields.Selection(string='Text Formate',
                            selection=[('short_text', 'Short Text'), ('long_text', 'Long Text')])

    related_model = fields.Many2one('ir.model', string="Model Name")
    delimiter = fields.Char("Delimiter")
    columns_ids = fields.One2many('text.generation_fields', 'model_id', string='Text Column')

    _sql_constraints = [
        ('name_related_model_uniq', 'unique(name, related_model)',
         'This is already available'),
    ]
