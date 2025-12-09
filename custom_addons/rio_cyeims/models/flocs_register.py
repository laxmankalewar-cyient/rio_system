import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class FlocsRegister(models.Model):
    _name = "flocs.register"
    _description = "Flocs Register"
    _rec_name = 'floc_id'

    pu_id = fields.Many2one('rio.pu', 'PU')
    site = fields.Many2one('rio.site', related='pu_id.site', store=True)
    site_name = fields.Char(related='site.name', string="Site Name", store=True)
    pu_desc = fields.Char('PU Desc', related='pu_id.description', readonly=True)
    floc_id = fields.Many2one('rio.flocs', 'FLOC')
    flocs_desc = fields.Char('Flocs Desc', related='floc_id.description', readonly=True)

    parent_relation = fields.Selection(string='Parent / Child',
                                       selection=[('parent_only', 'Parent Only'), ('parent', 'Parent'),
                                                  ('child', 'Child'), ('parent_with_drawings', 'Parent with Drawings')],
                                       default='parent_only')
    process_area = fields.Many2one(related = 'floc_id.process_area', string='Process Area')
    asset_type = fields.Many2one(related= 'floc_id.asset_type', string='Asset Type')
    criticality = fields.Char('Criticality', related='floc_id.criticality', readonly=True)

    #detail_drawings = fields.Char('Detail Drawings')
    detail_drawings = fields.Char('DWG Liner Detail')
    #layout_drawings = fields.Char('Layout Drawings')
    layout_drawings = fields.Char('DWG Marking Plan')
    sum_of_liner = fields.Html('Sum of Liners')
    count_of_liner = fields.Html('Count of Liners')

    _sql_constraints = [
        ('floc_liner_detailed_drawing_uniq', 'unique(floc_id, detail_drawings,layout_drawings)',
         'Floc and liner combination already added.'),
    ]


    def find_parent_flocs(self, all_flocs):
        proper_prefixes = set()
        for i in range(len(all_flocs)):
            for j in range(len(all_flocs)):
                if i != j and all_flocs[j].startswith(all_flocs[i]) and len(all_flocs[i]) < len(all_flocs[j]):
                    proper_prefixes.add(all_flocs[i])
        return list(proper_prefixes)

    def parent_child_relation_flocs(self, args):
        force_update = args.get('force_update', False)
        domain = [('parent_relation', '=', False), ('floc_id', 'not in', ['Floc not found','Unkown'])]
        if force_update:
            domain = [('floc_id', 'not in', ['Floc not found', 'Unkown'])]
        flocs = self.search(domain)
        flocs.write({'parent_relation':'parent_only'})
        all_flocs = [floc.floc_id.name for floc in flocs]
        parent_flocs = self.find_parent_flocs(all_flocs)

        for floc in parent_flocs:
            res = self.search([('floc_id', 'ilike', floc)])
            for re in res:
                if re.floc_id.name == floc:
                    re.write({'parent_relation': 'parent'})
                else:
                    re.write({'parent_relation': 'child'})

    def remove_flocs_register(self):
        flocs_registers = self.env['flocs.register'].read_group(
            [('detail_drawings', '!=', 'NA'), ('layout_drawings', '!=', 'NA')],
            ['floc_id', 'detail_drawings', 'layout_drawings'],
            ['floc_id', 'detail_drawings', 'layout_drawings'], lazy=False)
        for flocs_register in flocs_registers:
            floc_id = flocs_register['floc_id'][0]
            detail_drawings = flocs_register['detail_drawings']
            dwg_markingplan = flocs_register['layout_drawings']
            liner_tax = self.env['product.liner_taxonomy'].search([('floc_id', '=', floc_id),
                                                                   ('dwg_linerdetail', '=', detail_drawings),
                                                                   ('dwg_markingplan', '=', dwg_markingplan)])
            if liner_tax:
                continue
            else:
                flocs_reg = self.env['flocs.register'].search(flocs_register['__domain'])
                flocs_reg.unlink()

    def add_flocks(self, params=None):
        if params is None:
            params = {}
        limit = params.get('limit', 1)
        domain = params.get('domain', [])
        for floc in self.env['rio.flocs'].search(domain):
            taxonomy = self.env['product.liner_taxonomy'].read_group(
                [('floc_id', '=', floc.id)], ['liner_detail_qty', 'dwg_linerdetail', 'dwg_markingplan'],
                ['floc_id', 'dwg_linerdetail', 'dwg_markingplan'],
                lazy=False)
            if not taxonomy:
                val = {"floc_id": floc.id, "pu_id": floc.pu_id.id, 'detail_drawings': 'NA',
                       'layout_drawings': 'NA'}

                floc_register = self.search([('floc_id', '=', floc.id), ('detail_drawings', '=', 'NA')])
                if floc_register:
                    floc_register.write(val)
                else:
                    floc_register.create(val)

            for line in taxonomy:
                detail_drawings = line["dwg_linerdetail"]
                dwg_markingplan = line["dwg_markingplan"]

                val = {"floc_id": floc.id, "pu_id": floc.pu_id.id,
                       'layout_drawings': dwg_markingplan,
                       'count_of_liner': line["__count"],
                       "sum_of_liner": line["liner_detail_qty"], "detail_drawings": detail_drawings}

                domain_1 = [
                    ('floc_id', '=', floc.id),

                    '|',
                    ('detail_drawings', '=', detail_drawings),
                    ('detail_drawings', '=', 'NA'),

                    '|',
                    ('layout_drawings', '=', dwg_markingplan),
                    ('layout_drawings', '=', 'NA'),
                ]

                floc_register = self.search(domain_1)
                if floc_register:
                    floc_register.write(val)
                else:
                    floc_register.create(val)
        self._cr.commit()
        self.remove_flocs_register()
