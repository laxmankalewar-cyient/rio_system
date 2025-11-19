from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class RioAssetType(models.Model):
    _name = "rio.asset_type"
    _description = "Rio Process Area"
    _rec_name = "name"

    name = fields.Char("Name")
    _sql_constraints = [
        ('asset_type_uniq', 'unique(name)',
         'Asset Type is already added.'),
    ]


class RioProcessArea(models.Model):
    _name = "rio.process_area"
    _description = "Rio Process Area"
    _rec_name = "name"

    name = fields.Char("Name")
    _sql_constraints = [
        ('process_area_uniq', 'unique(name)',
         'This Process Area is already added.'),
    ]


class RioAssetDashboard(models.Model):
    _name = "rio.asset_dashboard"
    _description = "Rio Asset Dashboard"
    _rec_name = "floc_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    site = fields.Many2one('rio.site', required=True)
    floc_id = fields.Many2one('rio.flocs', 'FLOC')
    criticality = fields.Selection([
        ('crit_1', '1'),
        ('crit_2', '2'),
        ('crit_3', '3'),
        ('crit_4', '4'),
        ('crit_5', '5'),
        ('crit_end', 'End')
    ], string='Criticality')
    process_area = fields.Many2one('rio.process_area', string='Process Area')
    asset_type = fields.Many2one('rio.asset_type', string='Asset Type')
    num_taxo_lines = fields.Integer("Liners Entries")

    total_liners = fields.Integer(string="Total Liners", help="Total count of installed Liners")
    uniq_liners = fields.Integer(string="Unique Liners", help="Unique Liners Installed")

    sap_mtr_identified = fields.Integer(string="SAP Material Identified")
    new_mtr_required = fields.Integer(string="New Materials Required")
    sap_mtr_update = fields.Integer(string="Existing SAP Material Update")
    active = fields.Boolean(string='active', default=True)

    _sql_constraints = [
        ('floc_site_uniq', 'unique(floc,site)',
         'This FLOC is already added.'),
    ]

    def action_update_dashboard_floc_records(self, site_id):
        liner_taxonomy = self.env['product.liner_taxonomy']

        for record in self.search([('site', '=', site_id)]):
            total_liners = 0
            sap_materials = []
            unique_rtio_liner_codes = []
            num_taxo_lines = 0

            taxonomy_records = liner_taxonomy.search([('floc_id', '=', record.floc_id.id), ('site', '=', site_id)])
            for taxonomy_record in taxonomy_records:
                total_liners = total_liners + taxonomy_record.liner_detail_qty
                num_taxo_lines = num_taxo_lines + 1

                if taxonomy_record.rtio_liner_code not in unique_rtio_liner_codes:
                    unique_rtio_liner_codes = unique_rtio_liner_codes + [taxonomy_record.rtio_liner_code]

                sap_material = taxonomy_record.sap_material.strip()
                if sap_material and sap_material != 'NA' and sap_material not in sap_materials:
                    sap_materials = sap_materials + [sap_materials]

            uniq_liners = len(unique_rtio_liner_codes)

            sap_mtr_identified = len(sap_materials)
            new_mtr_required = max(uniq_liners - sap_mtr_identified, 0)
            sap_mtr_update = sap_mtr_identified

            record.write({'num_taxo_lines': num_taxo_lines,
                          'total_liners': total_liners,
                          'uniq_liners': uniq_liners,
                          'sap_mtr_identified': sap_mtr_identified,
                          'new_mtr_required': new_mtr_required,
                          'sap_mtr_update': sap_mtr_update})

        return True

    def action_create_dashboard_records(self, site_id):
        liner_taxonomy = self.env['product.liner_taxonomy']
        result = liner_taxonomy.read_group([('site', '=', site_id)], fields=['floc_id'],
                                           groupby=['floc_id'], orderby='id')
        flocs = []
        counter = 0
        for r in result:

            if not r['floc_id']:
                continue
            floc_id = r['floc_id'][0]
            floc = self.search([('floc_id', '=', floc_id), ('site', '=', site_id)])
            if not floc:
                flocs = flocs + [{'floc_id': floc_id, 'site': site_id}]
                counter = counter + 1
                res = self.create(flocs)
                flocs = []
                if counter > 3:
                    counter = 0
                    _logger.info(f"{len(res)}/{len(result)} FLOCs record created.")
                    self._cr.commit()
        self._cr.commit()
        return True
