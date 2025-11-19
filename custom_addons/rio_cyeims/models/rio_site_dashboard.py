from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)
NEW_EXISTING_MATERIAL = {'new_material': 'Create New Material in SAP',
                         'existing_no_match': 'Material Found in SAP But Not in Taxonomy',
                         'existing_flocs_mismatch': 'Material Found in SAP Under A Different FLOC in Taxonomy',
                         'add': 'Assign Existing SAP Material to The FLOC',
                         'match': 'Material Matches both in Taxonomy and SAP',
                         'same_riocode_material': 'Assign Existing Material having same Riocode',
                         'undefined': 'Undefined'}


class RioSiteGraph(models.Model):
    _name = "rio.site_graph"
    _description = "Rio Site Graph"
    _rec_name = "site"
    site = fields.Many2one('rio.site', required=True)
    yandi_data = fields.Integer("Rio Site-Yandi Data")
    data_label = fields.Char("Data Label")


class RioDashboardFilterToUser(models.Model):
    _name = "rio.filter_dashboard_users"
    _description = "Rio Filter Of Dashboard Users Wise"
    _rec_name = "user_id"

    user_id = fields.Many2one('res.users', 'Users')
    site_dashboard_id = fields.Many2one('rio.site_dashboard')

    active = fields.Boolean(default=True)


class RioSiteDashboard(models.Model):
    _name = "rio.site_dashboard"
    _description = "Rio Site Dashboard"
    _rec_name = "site"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "sequence"

    sequence = fields.Integer("Seq")
    site = fields.Many2one('rio.site', required=True)
    global_site = fields.Boolean(related = 'site.global_site',)
    taxo_entries = fields.Integer("Taxonomy Entries")
    repeated_liner = fields.Integer(string='Repeated Liners')
    unique_liner = fields.Integer(string='Unique Liner')
    unique_with_na = fields.Integer(string='Unique Liner with NA')
    unique_with_material = fields.Integer(string='Unique Liner with Material')
    rtio_multiple_mtr = fields.Integer(string='Rio Code with Multiple Materials')
    material_count = fields.Integer(string='Duplicate Materials Count')
    new_mtr_required = fields.Integer(string='New Materials Required')
    sap_mtr_identified = fields.Integer(string='SAP Material Identified')

    pu_identified = fields.Integer(string='PUs Identified')
    flocs_identified = fields.Integer(string='FLOCs Drawing Identified')

    layout_drawings = fields.Integer(string='Layout drawings')
    detailed_drawings = fields.Integer(string='Detailed Drawings')
    active = fields.Boolean(string='active', default=True)
    visible_dashboard = fields.Boolean(string='visible In Dashboard', default=False)

    flocs_det_drw_not_identified = fields.Integer(string='FLOCs Drawing Not Identified')
    filter_users = fields.One2many('rio.filter_dashboard_users', 'site_dashboard_id')

    same_riocode_with_na = fields.Integer(string='Same Rio Code with NA and Material')
    riocode_repeated_multi_same_material = fields.Integer(string='Riocode repeated multi times with same Material')
    riocode_multi_mat_without_na = fields.Integer(string='Riocode with multi Material without NA')
    riocode_multi_mat_with_na = fields.Integer(string='Riocode with multi Material with NA')

    _sql_constraints = [
        ('site_uniq', 'unique(site)',
         'This Site is already added.'),
    ]

    @api.model
    def get_canvas_existing_material(self):
        model_name = self.env['taxonomy.bom_structure']

        taxonomy_data = model_name.read_group([], ['new_existing_material'], ['new_existing_material'])
        existing_material_status = []
        count = []
        for existing_material in NEW_EXISTING_MATERIAL.keys():
            existing_material_status.append(NEW_EXISTING_MATERIAL.get(existing_material))
            flg = False
            for taxonomy in taxonomy_data:
                if taxonomy.get('new_existing_material', '') == existing_material:
                    count.append(taxonomy.get('new_existing_material_count', 0))
                    flg = True
                    break
            if not flg:
                count.append(0)
        return {'status': existing_material_status, 'count': count}


    def execute_all_action_update_dashboard_site_records(self, site_id=None):
        domain = []
        if site_id:
            domain = [('site', '=', site_id)]
        dashboard_sites = self.search(domain)
        for dashboard in dashboard_sites:
            self.action_update_dashboard_site_records(dashboard.site.id)

    @api.model
    def save_filter_sites(self, user_id, sites_name):
        user_given_filters = self.env['rio.site_dashboard'].sudo().search([('id', 'in', sites_name)])

        user_with_selected_site = self.env['rio.filter_dashboard_users'].sudo().search(
            [('user_id', '=', user_id), ('active', 'in', [True, False])])
        user_with_selected_site.write({'active': False})
        for s_site in user_given_filters:
            flag = True
            for user_site in user_with_selected_site:
                if user_site.site_dashboard_id.id == s_site.id:
                    user_site.write({'active': True})
                    flag = False
                    break
            if flag:
                if s_site.id not in user_with_selected_site.site_dashboard_id.ids:
                    self.env['rio.filter_dashboard_users'].sudo().create(
                        {'user_id': user_id, 'site_dashboard_id': s_site.id})
        return True

    @api.model
    def get_all_sites(self, vals):
        user_with_selected_site = self.env['rio.filter_dashboard_users'].sudo().search([('user_id', '=', vals)])
        all_sites = self.env['rio.site_dashboard'].sudo().search([])
        site_data = []
        site_arr_ids = []
        for s_site in user_with_selected_site:
            if not s_site.site_dashboard_id.id in site_arr_ids:
                sites_disc = {'site_id': s_site.site_dashboard_id.id, 'site_name': s_site.site_dashboard_id.site.name,
                              'is_selected': True}
                site_data.append(sites_disc)
                site_arr_ids.append(s_site.site_dashboard_id.id)

        for site in all_sites:
            if not site.id in site_arr_ids:
                sites_disc = {'site_id': site.id, 'site_name': site.site.name, 'is_selected': False}
                site_data.append(sites_disc)
                site_arr_ids.append(site.id)

        return site_data

    @api.model
    def get_new_material_created_and_required(self):
        bom_records = self.env['taxonomy.bom_structure'].search([('new_existing_material', '=', 'new_material')])

        site_map = {}
        for record in bom_records:
            site = record.site
            if not site:
                continue
            site_name = site.short_text or site.name
            site_entry = site_map.setdefault(site_name, {
                'rio_codes': set(),
                'new_material_numbers': set()
            })
            if record.rio_code:
                site_entry['rio_codes'].add(record.rio_code.strip().upper())
            if record.new_material_number:
                site_entry['new_material_numbers'].add(record.new_material_number)

        sites = []
        new_material_creation_required = []
        new_material_created = []

        for site_name, data in site_map.items():
            sites.append(site_name)
            new_material_creation_required.append(len(data['rio_codes']))
            new_material_created.append(len(data['new_material_numbers']))

        return {
            'name': sites,
            'new_material_creation_required': new_material_creation_required,
            'new_material_created': new_material_created
        }
    @api.model
    def get_canvas_taxonomy_bom_status(self):
        model_name = self.env['taxonomy.bom_structure']
        bom_status = []
        for field_name, field_obj in model_name.sudo()._fields.items():
            if field_name == 'bom_status' and isinstance(field_obj, fields.Selection):
                bom_status.extend(field_obj.selection)
                break

        taxonomy_data = self.env['taxonomy.bom_structure'].read_group([], ['bom_status'], ['bom_status'])
        b_status = []
        count = []
        for status in bom_status:
            b_status.append(status[1])
            flg = False
            for taxonomy in taxonomy_data:
                if taxonomy.get('bom_status', '') == status[0]:
                    count.append(taxonomy.get('bom_status_count', 0))
                    flg = True
                    break
            if not flg:
                count.append(0)

        return {'status': b_status, 'count': count}

    @api.model
    def get_duplicate_materials(self):
        user_id = self.env.uid
        user_with_selected_site = self.env['rio.filter_dashboard_users'].sudo().search([('user_id', '=', user_id)])
        rio_sites = self.search([('id', 'in', user_with_selected_site.site_dashboard_id.ids)])
        sites = []
        count = []
        for obj in rio_sites:
            site_name = obj.site.short_text if obj.site.short_text else obj.site.name
            sites.append(site_name)
            count.append(obj.material_count)
        return {'name': sites, 'count': count}

    @api.model
    def get_site_with_unique_liner(self):
        user_id = self.env.uid
        user_with_selected_site = self.env['rio.filter_dashboard_users'].sudo().search([('user_id', '=', user_id)])
        rio_sites = self.search([('id', 'in', user_with_selected_site.site_dashboard_id.ids)])
        sites = []
        unq_count = []
        for obj in rio_sites:
            site_name = obj.site.short_text if obj.site.short_text else obj.site.name
            sites.append(site_name)
            unq_count.append(obj.unique_liner)
        return {'sites': sites, 'count': unq_count}

    @api.model
    def get_sites_with_flocs_identified_and_det_drw_not_identified(self):
        user_id = self.env.uid
        user_with_selected_site = self.env['rio.filter_dashboard_users'].sudo().search([('user_id', '=', user_id)])
        rio_sites = self.search([('id', 'in', user_with_selected_site.site_dashboard_id.ids)])
        sites = []
        flocs_identified = []
        flocs_det_drw_not_identified = []
        for obj in rio_sites:
            site_name = obj.site.short_text if obj.site.short_text else obj.site.name
            sites.append(site_name)
            flocs_identified.append(obj.flocs_identified)
            flocs_det_drw_not_identified.append(obj.flocs_det_drw_not_identified)
        return [sites, flocs_identified, flocs_det_drw_not_identified]

    @api.model
    def get_sites_sap_mtr_with_new_mtr_required(self):
        user_id = self.env.uid
        user_with_selected_site = self.env['rio.filter_dashboard_users'].sudo().search([('user_id', '=', user_id)])
        rio_sites = self.search([('id', 'in', user_with_selected_site.site_dashboard_id.ids)])
        sites = []
        sap_mtr_identified = []
        new_mtr_required = []
        for obj in rio_sites:
            site_name = obj.site.short_text if obj.site.short_text else obj.site.name
            sites.append(site_name)
            sap_mtr_identified.append(obj.sap_mtr_identified)
            new_mtr_required.append(obj.new_mtr_required)

        return [sites, sap_mtr_identified, new_mtr_required]

    @api.model
    def get_site_details(self):
        user_id = self.env.uid
        user_with_selected_site = self.env['rio.filter_dashboard_users'].sudo().search([('user_id', '=', user_id)])
        rio_sites = self.search([('visible_dashboard', '=', True),
                                 ('id', 'in', user_with_selected_site.site_dashboard_id.ids)])
        result = []
        for obj in rio_sites:
            vals = [obj.site.id, obj.site.name, obj.taxo_entries, obj.unique_liner,
                    obj.repeated_liner, obj.flocs_identified, obj.rtio_multiple_mtr,
                    obj.unique_with_na, obj.unique_with_material, obj.site.global_site,
                    obj.same_riocode_with_na, obj.riocode_repeated_multi_same_material,
                    obj.riocode_multi_mat_without_na, obj.riocode_multi_mat_with_na]
            result.append(vals)
        return result

    def action_update_dashboard_site_records(self, site_id):
        domain = [('site', '=', site_id)]
        return self.action_update_dashboard_site_records_with_domain(domain, site_id)

    def action_update_dashboard_site_records_with_domain(self, domain, site_id):
        liner_taxonomy = self.env['product.liner_taxonomy']
        site_dashboard_record = self.search([('site', '=', site_id)])[0]
        taxo_entries = liner_taxonomy.search_count(domain)
        unique_liner = liner_taxonomy.read_group(domain, fields=['rtio_liner_code'],
                                                 groupby=['rtio_liner_code'])

        t_unique_liner = [u_liner.get('rtio_liner_code') for u_liner in unique_liner if
                          u_liner.get('rtio_liner_code_count') == 1]
        new_domain = domain + [('rtio_liner_code', 'in', t_unique_liner), ('sap_material', '!=', 'NA')]

        unique_liner = len(t_unique_liner)
        unique_with_material_count = liner_taxonomy.search_count(new_domain)
        unique_with_na_count = unique_liner - unique_with_material_count

        repeated_liner = taxo_entries - unique_liner

        sap_materials = []
        flocs_identified = []
        pu_identified = []
        layout_drawings = []
        detailed_drawings = []
        rtio_multiple_mtr = {}
        flocs_det_drw_not_identified = 0

        if site_dashboard_record.site.global_site:
            query = (f"SELECT COUNT(DISTINCT floc_id) AS floc_id_count FROM flocs_register"
                     f" WHERE (detail_drawings IS NULL OR detail_drawings = '' OR detail_drawings = 'NA' OR detail_drawings = 'na')")
        else:
            query = (f"SELECT COUNT(DISTINCT floc_id) AS floc_id_count FROM flocs_register"
                     f" WHERE (detail_drawings IS NULL OR detail_drawings = '' OR detail_drawings = 'NA' OR detail_drawings = 'na')"
                     f" AND site={site_id}")

        cr = self.env.cr
        cr.execute(query)
        data = cr.fetchall()
        flocs_not = [d[0] for d in data]
        if len(flocs_not) >= 1:
            flocs_det_drw_not_identified = flocs_not[0]

        for record in liner_taxonomy.search(domain):

            floc = record.floc_id.name.strip() if record.floc_id else 'undefined'
            if floc and floc.lower() not in ['floc not found', 'unkown', 'undefined'] and floc not in flocs_identified:
                dwg_linerdetail = record.dwg_linerdetail.strip() if record.floc_id else 'NA'
                if dwg_linerdetail != 'NA':
                    flocs_identified = flocs_identified + [floc]

            pu = record.pu_id.name.strip() if record.floc_id else 'undefined'
            if pu and pu.lower() != 'undefined' and pu not in pu_identified:
                pu_identified = pu_identified + [pu]

            sap_material = record.sap_material if record.sap_material.strip() and record.sap_material != 'NA' else False
            if sap_material:
                if record.rtio_liner_code in rtio_multiple_mtr:
                    if sap_material not in rtio_multiple_mtr[record.rtio_liner_code]:
                        rtio_multiple_mtr[record.rtio_liner_code] = rtio_multiple_mtr[record.rtio_liner_code] + [
                            sap_material]
                else:
                    rtio_multiple_mtr[record.rtio_liner_code] = [sap_material]

            if sap_material and sap_material not in sap_materials:
                sap_materials = sap_materials + [sap_material]

            dwg_markingplan = record.dwg_markingplan and record.dwg_markingplan.strip()
            if dwg_markingplan and dwg_markingplan.lower() != 'undefined' and dwg_markingplan not in layout_drawings:
                layout_drawings = layout_drawings + [dwg_markingplan]

            dwg_linerdetail = record.dwg_linerdetail and record.dwg_linerdetail.strip()
            if dwg_linerdetail and dwg_linerdetail.lower() != 'undefined' and dwg_linerdetail not in detailed_drawings:
                detailed_drawings = detailed_drawings + [dwg_linerdetail]

        new_mtr_required = max(unique_liner - len(sap_materials), 0)
        sap_mtr_identified = len(sap_materials)

        count_rtio_multiple_mtr = 0
        material_count = 0
        for k, v in rtio_multiple_mtr.items():
            if len(v) > 1:
                count_rtio_multiple_mtr = count_rtio_multiple_mtr + 1
                material_count = material_count + len(v)
        vals = {'taxo_entries': taxo_entries,
                'repeated_liner': repeated_liner,
                'unique_liner': unique_liner,
                'unique_with_na': unique_with_na_count,
                'unique_with_material': unique_with_material_count,
                'rtio_multiple_mtr': count_rtio_multiple_mtr,
                'material_count': material_count,
                'new_mtr_required': new_mtr_required,
                'sap_mtr_identified': sap_mtr_identified,
                'pu_identified': len(pu_identified),
                'flocs_identified': len(flocs_identified),
                'detailed_drawings': len(detailed_drawings),
                'layout_drawings': len(layout_drawings),
                'flocs_det_drw_not_identified': flocs_det_drw_not_identified
                }
        if site_dashboard_record.site.global_site:
            liner_taxonomy.compute_group_by_greater_than_one()
            vals['same_riocode_with_na'] = liner_taxonomy.search_count(
                [('rtio_liner_code_greater_one', '=', 'Same RIO-Code With NA')])
            total_count, total_count_matnr_na = self.get_material_riocode_counts()
            vals['riocode_repeated_multi_same_material'] = total_count
            vals['riocode_multi_mat_with_na'] = total_count_matnr_na
            vals['riocode_multi_mat_without_na'] = self.export_sql_results_to_file()

        ret = site_dashboard_record.write(vals)
        return ret

    def get_material_riocode_counts(self):
        total_count = 0
        total_count_matnr_na = 0
        self.env.cr.execute("""
                SELECT rtio_liner_code, COUNT(rtio_liner_code), MAX(sap_material) AS sap_material 
                FROM product_liner_taxonomy
                GROUP BY rtio_liner_code HAVING COUNT(DISTINCT sap_material) = 1;
            """)
        results = self.env.cr.fetchall()

        for row in results:
            rio_code, count, material = row
            if material == 'NA':
                if count > 1:
                    total_count_matnr_na += count
                continue
            if count <= 1:
                continue
            total_count += count
        return total_count, total_count_matnr_na

    def export_sql_results_to_file(self):
        total_count = 0
        self.env.cr.execute("""
            SELECT  rtio_liner_code, COUNT(rtio_liner_code) AS total_count,
            STRING_AGG(DISTINCT sap_material, ', ') AS all_sap_materials
            FROM product_liner_taxonomy
            GROUP BY rtio_liner_code
            HAVING COUNT(DISTINCT sap_material) > 1;

        """)
        results = self.env.cr.fetchall()

        for row in results:
            rtio_liner_code, RIOCODE_Count, sap_material = row
            sap_material_list = [item.strip() for item in sap_material.split(',')]
            if 'NA' in sap_material_list:
                continue
            total_count += RIOCODE_Count

        return total_count


