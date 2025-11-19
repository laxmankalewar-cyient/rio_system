import logging
import re,  openpyxl
import base64
from odoo import api, fields, models, tools, _, exceptions
import csv, os
import pandas as pd
from datetime import datetime
from collections import OrderedDict

_logger = logging.getLogger(__name__)


class LinerFiles(models.Model):
    _name = "product.liner_file"
    _description = "Product Liner File"
    _rec_name = 'file_name'

    file_id = fields.Many2one('dms.file', string="Input File")
    file_name = fields.Char(related="file_id.name")
    log = fields.Html("Log")
    is_bom_file = fields.Boolean("Is BOM Files")
    site = fields.Many2one('rio.site', required=True)
    output_file = fields.Many2one('dms.file', string="Output Files")
    is_output = fields.Boolean(default=False)

    def action_process_data(self):
        logs = ''
        if self.is_bom_file:
            logs = self.process_bom_data()
        else:
            file_path = self.file_id.get_dms_file_path()
            destination_file = self.file_id.copy_file_to_temp_dir(file_path, self.file_id.name)
            logs = self.env['product.liner_taxonomy'].read_xlsx_to_dict(destination_file)
        self.write({'log':logs})

    def process_bom_data(self):
        file_path = self.file_id.get_dms_file_path()
        input_file = self.file_id.copy_file_to_temp_dir(file_path, self.file_id.name)

        temp_dir = self.file_id.get_dms_temp_dir()
        if not temp_dir:
            raise exceptions.UserError(f"Provide The Temp Directory")
        file_name = os.path.splitext(self.file_id.name)[0]
        date = datetime.now().strftime('%Y%m_%d%H%M%S')
        file_name = f"{file_name}_{date}.xlsx"
        output_dir_id = self.file_id.directory_id.id
        output_file = os.path.join(temp_dir, file_name)
        site_code = self.site.code
        self.read_file(input_file, site_code, output_file)
        self.create_output_dms_file(output_file, file_name, output_dir_id)
        return ''

    def create_update_bom_data(self):
        if not self.output_file:
            raise exceptions.UserError(f"Output File is not Generated")
        file_path = self.output_file.get_dms_file_path()
        output_file = self.file_id.copy_file_to_temp_dir(file_path, self.output_file.name)

        workbook = openpyxl.load_workbook(output_file)
        sheet = workbook.active

        headers = [cell for cell in sheet.iter_rows(min_row=1, max_row=1, values_only=True)]
        headers = list(headers[0])
        headers = [x.replace(' ', '_').title() if x else None for x in headers]
        logs=""

        def normalise(v):
            if isinstance(v, str):
                return v.replace("\xa0", " ").strip()

            if isinstance(v, int):
                return str(v)
            return v
        count = 0
        for row in sheet.iter_rows(min_row=2):

            row_data = {headers[col_index].lower(): normalise(cell.value) for col_index, cell in enumerate(row)}

            bom = self.env['ih01.bom_data'].search([('pu', '=', row_data.get('pu')),
                                                    ('navi_pu', '=', row_data.get('parent_pu')),
                                                    ('floc', '=', row_data.get('floc')),
                                                    ('material', '=', row_data.get('material')),
                                                    ('parent_pma', '=', row_data.get('parent_pma')),
                                                    ('pma', '=', row_data.get('pma')),
                                                    ('ct', '=', row_data.get('ct')),
                                                    ('site', '=', self.site.id)])
            row_data['site'] = self.site.id
            if bom:
                logs += f"Re-Write PMA = {row_data.get('pma')} - {row_data.get('material')}<br>"
                #print(logs)
                continue
            else:
                self.env['ih01.bom_data'].create(row_data)
            count += 1
            if count > 1000:
                self._cr.commit()
                count = 0

        self.write({'log':logs})

    def create_output_dms_file(self, file_path, file_name, output_dir_id):

        if file_path:
            with open(file_path, "rb") as file:
                binary_content = file.read()

        content = base64.b64encode(binary_content)

        vals = {"content": content,
                "directory_id": output_dir_id, "name": file_name}
        dms_id = self.env['dms.file'].sudo().create(vals)

        dms_id._cr.commit()

        if self.output_file:
            self.output_file.unlink()

        self.write({'output_file':dms_id,'is_output':True})

        if os.path.exists(file_path):
            os.remove(file_path)

    def read_file(self, input_data_file, site_code, output_file):
        lines = []
        i = 0
        with open(input_data_file, 'r') as file:
            for line in file:
                i = i + 1
                if i < 4:
                    continue
                line = line.strip('\n')
                if not line:
                    continue
                if line.startswith("X\t"):
                    line = line[2:]
                else:
                    line = line[1:]
                lines = lines + [line]

        hierarchy = self.parse_hierarchy(lines, site_code)
        self.write_dict_list_to_csv(hierarchy, output_file)
        return True

    def process_item_for_column_values(self, items, site_code):
        columns = OrderedDict(
            {'Navi PU': '', 'Navi PU Desc': '', 'PU': '', 'PU Desc': '', 'Parent FLOC': '', 'Parent FLOC Desc': '',
             'FLOC': '', 'FLOC Desc': '', 'CT': '', 'CT Desc': '', 'Parent PMA': '', 'PMA': '', 'PMA Desc': '', 'Material': '',
             'Material Desc': '', 'Material Qty': '', 'Material Unit': ''})

        separator = ", "
        navi_index = 0
        current_index = 0
        for item in items:
            main_object = item.get("main_object")
            level = item["level"]
            description = item.get("description").split("\t")
            description = [x.strip() for x in description]
            description = [x for x in description if x]

            current_index = current_index + 1
            navis = main_object.split("-")
            if len(navis) > 1:
                columns["Navi PU"] = main_object
                columns["Navi PU Desc"] = " ".join(description)
                navi_index = navi_index + 1
                continue
            elif current_index == navi_index + 1:
                columns["PU"] = main_object
                columns["PU Desc"] = " ".join(description)
            elif main_object.startswith("2") or main_object.startswith("4"):
                columns["Material"] = main_object
                columns["Material Desc"] = description[0]
                columns["Material Qty"] = description[len(description) - 2]
                columns["Material Unit"] = description[len(description) - 1]
            else:
                if main_object.startswith(site_code):
                    flocs = [floc for floc in items if
                             floc.get("level") > 1 and floc.get("main_object").startswith(site_code)]
                    if len(flocs) > 2:
                        flocs = flocs[-2:]
                    if len(flocs) > 1:
                        if flocs[0].get("level") == level:
                            columns["Parent FLOC"] = main_object
                            columns["Parent FLOC Desc"] = " ".join(description)
                        elif flocs[1].get("level") == level:
                            columns["FLOC"] = main_object
                            columns["FLOC Desc"] = " ".join(description)
                    else:
                        columns["FLOC"] = main_object
                        columns["FLOC Desc"] = " ".join(description)

                elif main_object.startswith("6"):

                    if len(description) >= 2 and description[1] == "I":

                        parent_pma = main_object + separator + (columns["Parent PMA"] if isinstance(columns["Parent PMA"],
                                                                        str) else '')
                        parent_pmas = parent_pma.strip(separator)
                        parent_pma_list = list(set(parent_pmas.split(separator)))
                        columns["Parent PMA"] = separator.join(parent_pma_list)
                        columns["PMA"] = main_object
                        columns["PMA Desc"] = " ".join(description)

                    else:
                        columns["CT"] = main_object
                        columns["CT Desc"] = " ".join(description)
        if columns["Parent PMA"] == columns["PMA"]:
            columns["Parent PMA"] = ''
        else:
            parent_pma_list = list(set(columns["Parent PMA"].split(separator)))
            parent_pma_list.remove(columns["PMA"])
            columns["Parent PMA"] = separator.join(parent_pma_list)
        return columns

    def parse_hierarchy(self, lines, site_code="3019"):
        bom = []
        for line in lines:
            indent_level = len(line) - len(line.lstrip('\t'))
            parts = line.strip().split('\t')
            main_object = parts[0]
            description = '\t'.join(parts[1:])  # Combine remaining elements as description
            item = {
                'level': indent_level,
                'main_object': main_object,
                'description': description.strip("\t").strip(),
            }
            bom = bom + [item]

        previous_level = 0
        item = {}
        bom_lines = []
        index = 0
        for line in bom:
            index = index + 1
            level = line['level']
            if level <= previous_level and previous_level > 0:
                new_item = [{k: v for k, v in item.items()}]
                bom_lines = bom_lines + new_item
                keys = list(item.keys())
                for key in keys:
                    if key > level:
                        del item[key]
            previous_level = level
            item[level] = line
        bom_lines = bom_lines + [item]

        sorted_bom = []
        csv_column_data = []
        for line in bom_lines:
            sorted_keys = sorted(line.keys())
            item = [line[key] for key in sorted_keys]
            column_values = self.process_item_for_column_values(item, site_code)
            csv_column_data = csv_column_data + [column_values]
            sorted_bom = sorted_bom + [item]
        return csv_column_data

    def write_dict_list_to_csv(self, dict_list, filename):
        df = pd.DataFrame(dict_list)
        numeric_cols = df.select_dtypes(include='number').columns
        df_numeric = df[numeric_cols].astype(int)
        sorted_numeric_cols = df_numeric.iloc[0].sort_values(ascending=False).index
        sorted_columns = sorted_numeric_cols.tolist() + list(df.columns.difference(numeric_cols))

        df = df[sorted_columns]
        df.fillna('', inplace=True)

        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
