import logging

from odoo import api, fields, models, tools, _
import openpyxl, io, base64

_logger = logging.getLogger(__name__)


class NewTaxonomyBOMStructure(models.Model):
    _inherit = "taxonomy.bom_structure"

    def action_calculate_BOM_from_liner_all_sites(self, site_ids=[]):
        for site_id in site_ids:
            _logger.info(f"Starting BOM schedule for site {site_id}")
            self.create_bom_from_liners(site_id)
            self.update_bom_from_liners(site_id)
            self.update_existing_flocs_mismatch_fields_bom_from_liner(site_id)
            self.re_change_create_new_material_in_sap_new(site_id)
            _logger.info(f"Finished BOM schedule for site {site_id}")

    def action_calculate_BOM_schedule(self, site_id):
        offset = 0
        limit = 500
        while True:
            res_data = self.env['ih01.bom_data'].search([('floc', 'ilike', 'CHU'), ('site', '=', site_id)],offset=offset, limit=limit)
            if not res_data:
                break
            for iho1 in res_data:
                self.create_bom_structure_new(iho1)
            offset += limit
            self._cr.commit()
            _logger.info(f"IH01 BOM processed: {offset}")
        self.add_parent_chut_flocs_new(site_id)
        self.create_bom_from_liners(site_id)
        self.update_bom_from_liners(site_id)
        self.update_existing_flocs_mismatch_fields_bom_from_liner(site_id)
        self.re_change_create_new_material_in_sap_new(site_id)

    def add_parent_chut_flocs_new(self, site_id):
        _logger.info("add_parent_chut_flocs_new: Started")
        ih01_data = self.env['ih01.bom_data'].read_group([('floc', 'ilike', 'CHU'),('parent_floc', 'ilike', 'CHU'),
             ('site', '=', site_id)],['floc', 'ct', 'pma', 'parent_floc'],['parent_floc'])

        for iho1_d in ih01_data:
            iho1 = self.env['ih01.bom_data'].search(iho1_d['__domain'], limit=1)
            vals = {
                'pma_description': self.get_str_val(iho1.pma_desc),
                'site': iho1.site.id,
                'package_unit': self.get_str_val(iho1.pu),
                'functional_location': self.get_str_val(iho1.parent_floc),
                'floc_description': self.get_str_val(iho1.parent_floc_desc),
                'parent_pma': self.get_str_val(iho1.parent_pma),
                'new_existing_material': 'undefined'
            }
            domain = [('site', '=', iho1.site.id),('package_unit', '=', vals['package_unit']),
                ('functional_location', '=', vals['functional_location']),
            ]
            existing = self.env['taxonomy.bom_structure'].search(domain, limit=1)

            if existing:
                _logger.info(f"Skipped duplicate parent FLOC: {vals['functional_location']}")
                continue

            self.env['taxonomy.bom_structure'].create(vals)
            _logger.info(f"Created parent FLOC BOM: {vals['functional_location']}")

        _logger.info("add_parent_chut_flocs_new: Completed")

    def create_bom_from_liners(self, site_id):
        offset = 0
        limit = 1000
        created_count = 0
        skipped_count = 0

        while True:
            liners = self.env['product.liner_taxonomy'].search([('site', '=', site_id)],offset=offset, limit=limit)
            if not liners:
                break

            for liner in liners:
                flocs = liner.floc_id.name
                material_number = liner.sap_material
                bom_liner = self.env['taxonomy.bom_structure'].search([('liner', '=', liner.id)], limit=1)
                if bom_liner:
                    skipped_count += 1
                    continue
                if material_number != 'NA':
                    ih01_bom = self.env['taxonomy.bom_structure'].search([
                        ('functional_location', '=', flocs),('material_number', '=', material_number)], limit=1)
                    if ih01_bom:
                        skipped_count += 1
                        continue
                if material_number != 'NA':
                    vals = {
                        'site': liner.site.id,
                        'package_unit': liner.pu_id.name,
                        'functional_location': flocs,
                        'floc_description': liner.floc_desc,
                        'material_number': liner.sap_material,
                        'pma': self.generate_pma(flocs),
                        'ct': self.generate_ct(flocs),
                        'liner': liner.id,
                        'new_existing_material': 'add'
                    }
                    vals = self.add_sap_t_code_vals(vals, material_number, flocs)
                else:
                    vals = {
                        'site': liner.site.id,
                        'package_unit': liner.pu_id.name,
                        'functional_location': flocs,
                        'floc_description': liner.floc_desc,
                        'material_number': self.generate_new_material(),
                        'pma': self.generate_pma(flocs),
                        'ct': self.generate_ct(flocs),
                        'liner': liner.id,
                        'new_existing_material': 'new_material'
                    }
                vals = self.add_liner_info(vals, [liner])
                self.env['taxonomy.bom_structure'].create(vals)
                created_count += 1
            offset += limit
            self._cr.commit()
            _logger.info(
                f"create_bom_from_liners processed: {offset}, created: {created_count}, skipped: {skipped_count}")

    def update_bom_from_liners(self, site_id):
        offset = 0
        limit = 1000
        updated_count = 0
        while True:
            liners = self.env['product.liner_taxonomy'].search([('site', '=', site_id)],offset=offset, limit=limit)
            if not liners:
                break
            for liner in liners:
                bom_liner = self.env['taxonomy.bom_structure'].search([('liner', '=', liner.id)], limit=1)
                if bom_liner:
                    vals = self.add_liner_info({}, [liner])
                    bom_liner.write(vals)
                    updated_count += 1
            offset += limit
            self._cr.commit()
            _logger.info(f"update_bom_from_liners processed: {offset}, updated: {updated_count}")

    def create_bom_structure_new(self, iho1):
        vals = {'pma_description': self.get_str_val(iho1.pma_desc),
                'material_description': self.get_str_val(iho1.material_desc),
                'material_qty': self.get_str_val(iho1.material_qty),
                'material_unit': self.get_str_val(iho1.material_unit), 'site': iho1.site.id,
                'package_unit': self.get_str_val(iho1.pu), 'functional_location': self.get_str_val(iho1.floc),
                'floc_description': self.get_str_val(iho1.floc_desc),
                'material_number': self.get_str_val(iho1.material), 'parent_pma': self.get_str_val(iho1.parent_pma),
                'pma': self.get_str_val(iho1.pma), 'ct': self.get_str_val(iho1.ct)}

        bom = self.env['taxonomy.bom_structure'].search([('package_unit', '=', self.get_str_val(iho1.pu)),
                                                         ('functional_location', '=', self.get_str_val(iho1.floc)),
                                                         ('material_number', '=', self.get_str_val(iho1.material)),
                                                         ('pma', '=', self.get_str_val(iho1.pma)),
                                                         ('ct', '=', self.get_str_val(iho1.ct)),])
        if iho1.material:
            liner_taxonomy = self.env['product.liner_taxonomy'].search(
                [('sap_material', '=', self.get_str_val(iho1.material)), ('site', '=', iho1.site.id)])
            if liner_taxonomy:
                status = self.get_material_status(liner_taxonomy, self.get_str_val(iho1.floc))
                if status == 'match':
                    liner_flocs = [liner for liner in liner_taxonomy if
                                   liner.floc_id.name == self.get_str_val(iho1.floc)]
                    vals = self.add_liner_info(vals, liner_flocs)
                elif status == 'existing_flocs_mismatch':
                    vals['material_where_used'] = self.get_flocs_as_str(liner_taxonomy)
                vals['new_existing_material'] = status
                liner_taxonomy.write({'is_exist_sap': True})
            else:
                vals['new_existing_material'] = 'existing_no_match'

            vals = self.add_sap_t_code_vals(vals, iho1.material, iho1.floc)
        else:
            vals['new_existing_material'] = 'undefined'

        if bom:
            vals['is_duplicate'] = True
            bom.write(vals)
            return bom
        else:
            self.env['taxonomy.bom_structure'].create(vals)

    def re_change_create_new_material_in_sap_new(self,site_id):
        bom_data = self.env['taxonomy.bom_structure'].read_group(
            [('new_existing_material', '=', 'new_material'), ('material_number', 'ilike', 'NEWMAT%') ,('site', '=', site_id) ], ['rio_code'],
            ['rio_code'])
        for bom in bom_data:
            bom_with_material = self.env['taxonomy.bom_structure'].read_group(
                [('rio_code', '=', bom['rio_code']), ('material_number', 'not ilike', 'NEWMAT%'),('site', '=', site_id)], ['rio_code'],
                ['rio_code'])
            # if bom_with_material:
            #     boms = self.env['taxonomy.bom_structure'].search(bom['__domain'])
            #     boms.write({'new_existing_material': 'same_riocode_material'})
            if bom_with_material:
                boms = self.env['taxonomy.bom_structure'].search([
                    ('rio_code', '=', bom['rio_code']),('new_existing_material', '=', 'new_material'),
                    ('material_number', 'ilike', 'NEWMAT%'),('site', '=', site_id)
                ])
                boms.write({'new_existing_material': 'same_riocode_material'})