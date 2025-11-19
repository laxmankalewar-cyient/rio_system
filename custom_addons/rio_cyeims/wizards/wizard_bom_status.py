from odoo import api, fields, models
from odoo.exceptions import UserError
import base64, io, xlsxwriter, logging

_logger = logging.getLogger(__name__)
SPARES_FINDER_HEADER = {
            "desired_transaction": "Desired transaction:",
            "sr_no": "Sr No.",
            "material_no": "Material number",
            "hers_no": "HERS number",
            "multiple_selection": "* Multiple Selection Creation Criteria This material is…",
            "additional_detail": "* Additional Details to support the Criteria:",
            "support_comments": "* Supporting comments:",
            "criticality_code": "*Criticality code",
            "material_type": "* Material Type",
            "plant": "* Plant",
            "storage_loc": "* Storage Location",
            "desc_english": "* Material description ENGLISH",
            "desc_other_lang": "Material description Language other than English.FILL IF NECESSARY",
            "purchase_order_eng": "*Purchase Order Text (Long material description) ENGLISH",
            "purchase_order_lang": "Purchase Order Text (Long material description) Language other than English FILL IF NECESSARY",
            "measure_unit": "* Base unit of measure (UOM)",
            "manufacturer_name": "* Manufacturer Name/ SAP Manufacturer code",
            "manufacturer_number": "* Manufacturer Part Number (MPN)",
            "article": "* Repairable article? Y/N",
            "processing_indicator": "Special Processing Indicator for repairables",
            "price": "Quoted price ( * )",
            "currency": "Currency",
            "value_usd": "Inventory value USD",
            "delivery_time": "Planned Delivery Time(Lead time in calendar days)",
            "drawing_number": "Drawing Number",
            "drawing_owner": "Owner of Drawing",
            "purchasing_group": "Purchasing Group",
            "val_class": "Valuation class",
            "key": "Key Noun / Modifier",
            "supplier": "Supplier",
            "supplier_number": "Supplier part number",
            "material_owner": "Material Owner",
            "material_fun_loc": "Functional Location",
            "material_group": "Material group",
            "replace_item": "Is this replacing an item already catalogued? Y/N",
            "disposal": "Previous Material Number and requirement for disposal if needed",
            "mrp_controller": "MRP controller (Materials Planner)",
            "mrp_type": "MRP Type",
            "lot_size": "Lot Size",
            "cc_phy_inv_ind": "CC phys. Inv. Ind",
            "procurement_type": "Procurement Type",
            "procurement_special": "Special Procurement",
            "stock_group": "Stock Determination Group",
            "check": "Availabity Check",
            "reorder_pt": "Reorder Point (ROP)",
            "stock_level": "Max. Stock Level",
            "comments": "Comments",
        }

SELECTION_STATUS = [('approved_to_add', 'Approved to Add'),  # 0
                    ('approved_to_update', 'Approved to Update'),  # 1
                    ('approved_to_delete', 'Approved to Delete'),  # 2
                    ('decline_to_delete', 'Decline To Delete'),  # 3
                    ('no_action', 'No Action Required'),  # 4
                    ('approved', 'Approved'),  # 5
                    ('decline', 'Decline'),  # 6
                    ]

SPARES_FINDER_HEADER_next_line = {
    "select": "Select from the drop down below.",
    "serial_no": "Serial number",
    "material_cr": "Material Creation: Material Master will provide number. Modification or -Extension: Please provide material number.",
    "material_creation": "Material Creation: Material Master will provide number.",
    "drop_selection": "Select from the drop down menu. Information on column F will populate as per your selection bellow.",
    "info": "Information on this column will populate as per your selection in the previous column E.",
    "answer_detail": "Provide answer to question populated in column E.",
    "criticality_mtr": "Criticality of Material (Click on star to consult 'Material Criticality Matrix').",
    "setting_type": "Default settings are Operating supplies (HIBE), other configurations available, Select a type:",
    "select_plant": "Select the required plant from drop down list. For multible plants, select 'All plants' or type plant numbers in the field",
    "storage_loc_no": "Specify storage location Number* Defaulted to main store 0001.",
    "english_desc": "Description ONLY of item is required. Limit of 40 Characters: Noun; Modifier; Attribute 1; Attribute 2",
    "other_lang_desc": "FILL IF NECESSARY Description ONLY of item is required. Limit of 40 Characters: Noun;Modifier; Attribute 1; Attribute 2",
    "purchase_order_text": "A purchase order text is a text describing the material in more detail. This text is subsequently copied to purchasing documents (such as purchase requisitions or purchase orders) automatically, where you can change it if necessary. It is valid for all organizational levels, not for a specific plant.",
    "purchase_order_desc": "A purchase order text is a text describing the material in more detail. This text is subsequently copied to purchasing documents (such as purchase requisitions or purchase orders) automatically, where you can change it if necessary. It is valid for all organizational levels, not for a specific plant.",
    "measure_select": "Select from the drop down below.",
    "manufacturer_sap": "Specify the SAP Manufacturer code and actual name of original manufacturer. If code des not exist put in full manufacturer name, URL link and country of origin.",
    "manufacture_no": "Specify the original manufacturer part number.",
    "material_article": "A material ordered can be New or Repairable. We should identify it, but the maintenance strategy will determine what we buy each time.",
    "processing_select": "Select from the drop down below.",
    "price_unit": "Provide unit price (e.g $ per KG)",
    "currency_select": "Select from the drop down below.",
    "value_currency": "Specify the value in USD as opposed to local currency. Not mandatory",
    "delivery_time_mt": "Determines the time it takes to obtain the material from the supplier until it gets to the warehouse. In calendar days.",
    "drawing_no": "Specifiy Drawing Number if required.",
    "drawing_owner": "If drawing number is provided then specifiy who owns the intellectual property of the drawing. Plant/Manufacturer/Engineering company?Please imput name of owner.",
    "purchasing_buyer": "Used to identify a buyer or a group of buyers who will process the purchase orders.",
    "val_class_mt": "Valuation classes are assigned to material types and are used in the automation of accounting entry determination. GL for Cost.",
    "key_select": "Select from the drop down below.",
    "supplier_SAP": "Specify the SAP vendor number (if available) and name of the supplier that will procure material.",
    "supplier_part_number": "Only if different than the actual Manufacturer Part Number.",
    "material_work": "Name the work centre, department or individual responsible for the material.",
    "fun_loc_mt": "Specify the equipment where the material is used.",
    "material_select": "Select from the drop down below.",
    "replace_item_part": "Is the item a replacement for an obsolete or superceded part? Yes/No",
    "replace_mtr": "Please advise what material number this is replacing and if known a preferred disposal method.",
    "mrp_controller_code": "Specifies the code of the MRP controller or group of MPR Controllers responsible for material planning for the material.Select from the drop down below.",
    "mrp_type": "SAP code that determines whether and how the material is planned.",
    "lot_size_mtr": "Determines which lot-sizing procedure the system uses within materials planning to calculate the quantity to be procured or produced.",
    "ind_group": "This indicator groups the materials together into various cycle counting categories.",
    "procurement_refer": "It refers to whether the material is procured internally or externally or can be procured in either way.",
    "procurement_allow": "Allows you to define the procurement type more exactly.",
    "stock_group_rule": "The stock determination group combined with the stock determination rule at plant level create a key for the stock determination strategy.",
    "sys_check": "The system checks for availability and generates requirements for materials planning.",
    "reorder_pt_mtr": "Specify Reorder Point. *Necesary unless material is on demand (DEM)",
    "stock_max": "Specify Max. Stock Level.",
    "stock_comments": "Specify any relevant comments for your Inventory Controller. Exe:Quantity of stock to return to inventory.Generic parts acceptable in a pinch. Etc.",
}


class WizardDmsFileMove(models.TransientModel):
    _name = "wizard.bom_status"
    _description = "Wizard BoM Status"

    bom_status = fields.Selection(string='BoM Status', selection="_get_category_selection")
    comment = fields.Text(string="Comments")

    @api.model
    def _get_category_selection(self):
        items = self.env["taxonomy.bom_structure"].read_group([('id', '=', self.env.context.get("active_ids"))],
                                                fields=['new_existing_material'], groupby=['new_existing_material'])
        if len(items) > 1:
            raise UserError(f"Multiple BoM Line Selection with Different New/Existing Material Status")

        status = items[0].get('new_existing_material', False)
        if not status:
            status = 'undefined'

        selection = []
        if status == 'new_material':
            selection.append(SELECTION_STATUS[5])
            selection.append(SELECTION_STATUS[6])
        elif status == 'existing_no_match':
            selection.append(SELECTION_STATUS[1])
            selection.append(SELECTION_STATUS[2])
            selection.append(SELECTION_STATUS[6])
        elif status == 'existing_flocs_mismatch':
            selection.append(SELECTION_STATUS[1])
            selection.append(SELECTION_STATUS[6])
        elif status == 'add':
            selection.append(SELECTION_STATUS[0])
            selection.append(SELECTION_STATUS[6])
        elif status == 'undefined':
            selection.append(SELECTION_STATUS[2])
            selection.append(SELECTION_STATUS[3])
            selection.append(SELECTION_STATUS[4])
        elif status == 'match':
            selection.append(SELECTION_STATUS[4])
            selection.append(SELECTION_STATUS[6])
        return selection

    def process(self):
        items = self.env["taxonomy.bom_structure"].browse(self.env.context.get("active_ids"))
        vals = {'bom_status': self.bom_status, 'comment': self.comment}
        items.write(vals)


class WizardBoMReport(models.TransientModel):
    _name = "wizard.bom_report"
    _description = "Wizard BoM Report"

    name = fields.Char(string="Spares Finder Name")

    def process_bom_report(self):
        bom_data = self.env["taxonomy.bom_structure"].browse(self.env.context.get("active_ids"))
        file_name = f'{self.name}.xlsx'
        res_id = self.env['spares.finder_report'].create({'name':file_name, 'is_system':True})
        output_data = self.create_xlsx_file_template_data(bom_data)
        attachment_id = self.env['ir.attachment'].create(
            {
                'name': file_name,
                'type': 'binary',
                'datas': output_data,
                'res_model': 'bom.report',
                'res_id': res_id.id
            })

        res_id.write({'spares_finder': [(6, 0, [attachment_id.id])]})

    def create_xlsx_file_template_data(self, bom_data):
        output = io.BytesIO()
        try:
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet()
            header_bold_style = workbook.add_format(
                {'text_wrap': True, 'bg_color': '#D9D9D9', 'font_color': '#000000', 'border': 1, "bold": 1,
                 "align": "center",
                 "valign": "vcenter"})
            link_plain_style = workbook.add_format(
                {'bg_color': '#FFFFFF', 'font_color': '#0037A4', 'border': 0, "bold": 1, "underline": 1,
                 "align": "center",
                 "valign": "vcenter"})
            blue_style = workbook.add_format({'bg_color': '#A0D2E0', 'font_color': '#000000', 'border': 1, "bold": 1})
            red_style = workbook.add_format({'bg_color': '#FDE9D9', 'font_color': '#F73C09', 'border': 1, "bold": 1})
            red_style_new = workbook.add_format(
                {'bg_color': '#FF0000', 'font_color': '#FFFFFF', 'border': 1, "bold": 1, "align": "center",
                 "valign": "vcenter"})
            pink_style = workbook.add_format(
                {'text_wrap': True, 'bg_color': '#CF4D4D', 'font_color': '#000000', 'border': 1, "bold": 1,
                 "align": "center",
                 "valign": "vcenter"})
            pink_style_left_align = workbook.add_format(
                {'bg_color': '#CF4D4D', 'font_color': '#000000', 'border': 1, "bold": 1, "valign": "vcenter"})
            pink_style_new = workbook.add_format(
                {'text_wrap': True, 'bg_color': '#E193A4', 'font_color': '#000000', 'border': 1, "bold": 1,
                 "align": "center",
                 "valign": "vcenter"})
            pink_style_new_left_align = workbook.add_format(
                {'bg_color': '#E193A4', 'font_color': '#000000', 'border': 1, "bold": 1, "valign": "vcenter"})
            light_pink_style = workbook.add_format(
                {'text_wrap': True, 'bg_color': '#F7CAC1', 'font_color': '#000000', 'border': 1, "bold": 1,
                 "align": "center",
                 "valign": "vcenter"})
            light_pink_style_left_align = workbook.add_format(
                {'bg_color': '#F7CAC1', 'font_color': '#000000', 'border': 1, "bold": 1, "valign": "vcenter"})

            plain_style = workbook.add_format(
                {'text_wrap': True, 'bg_color': '#FFFFFF', 'font_color': '#000000', 'border': 1, "align": "center"})
            only_border_style = workbook.add_format({'border': 1})
            header_bold_style.set_align('center')
            pink_style.set_align('center')
            pink_style_new.set_align('center')
            light_pink_style.set_align('center')
            red_style_new.set_align('center')
            pink_style.set_align('center')
            worksheet.set_column(0, 51, 20)
            worksheet.set_row(0, 35, '')
            worksheet.set_row(1, 30, '')
            worksheet.set_row(2, 30, '')
            worksheet.set_row(3, 65, '')
            worksheet.freeze_panes(0, 4)
            text_wrap_format = workbook.add_format(
                {'text_wrap': True, 'bg_color': '#FFFFFF', 'font_color': '#0037A4', 'border': 0, "bold": 1,
                 "underline": 1, "align": "center",
                 "valign": "vcenter"})
            hyperlink = 'Instructions Page (Change Language of document) / \n Page des Instructions (Changer la langue du document )'
            worksheet.merge_range("A1:D1", "", link_plain_style)
            worksheet.write_url('A1', hyperlink, text_wrap_format)
            worksheet.write('A2', 'Requestor Name:', blue_style)
            worksheet.merge_range("B2:D2", "", blue_style)
            worksheet.write('A3', '* Select Region:', red_style)
            worksheet.write('B3', 'RTIO', red_style_new)
            worksheet.merge_range("C3:D3", "", header_bold_style)
            worksheet.write('C3', 'Material Reference:', header_bold_style)
            worksheet.merge_range("E2:S3", "", pink_style)
            worksheet.merge_range("T2:AA3", "", pink_style_new)
            worksheet.write('T2', 'Additional BU Specific fields from End-User.Provide data available.',
                            pink_style_new_left_align)
            worksheet.merge_range("AB2:AT3", "", light_pink_style)
            worksheet.write('AB2', 'INVENTORY CONFIGURATION FIELDS.Provide if data available',
                            light_pink_style_left_align)
            worksheet.write('E2', '* MANDATORY FIELDS FOR REQUESTOR.', pink_style_left_align)

            for col, (key, value) in enumerate(SPARES_FINDER_HEADER.items()):
                if col < 4:
                    worksheet.write(3, col, value, header_bold_style)
                elif 4 <= col < 19:
                    if col == 12 or col == 14:
                        worksheet.write(3, col, value, pink_style_new)
                    else:
                        worksheet.write(3, col, value, pink_style)
                elif 19 <= col < 27:
                    worksheet.write(3, col, value, pink_style_new)
                else:
                    worksheet.write(3, col, value, light_pink_style)
            for col, (key, value) in enumerate(SPARES_FINDER_HEADER_next_line.items()):
                worksheet.write(4, col, value, plain_style)
            row_count = 6
            for bom_value in bom_data:
                worksheet.write(f'A{row_count}', "Creation", plain_style)
                worksheet.write(f'B{row_count}', row_count - 5, plain_style)
                worksheet.write(f'C{row_count}', "", only_border_style)
                worksheet.write(f'D{row_count}', "", only_border_style)
                worksheet.write(f'E{row_count}', "C. Material placed on a BOM for “as required” consumption",
                                plain_style)
                worksheet.write(f'F{row_count}', "C. What is the BOM number?", plain_style)
                worksheet.write(f'G{row_count}', "", only_border_style)
                worksheet.write(f'H{row_count}', "D - Minor maint. Impact", plain_style)
                worksheet.write(f'I{row_count}', "Operating Supplies (HIBE)", plain_style)
                worksheet.write(f'J{row_count}', bom_value.site.code, plain_style)
                worksheet.write(f'K{row_count}', "0001", plain_style)
                worksheet.write(f'L{row_count}', bom_value.sap_short_text, plain_style)
                worksheet.write(f'M{row_count}', "", only_border_style)
                worksheet.write(f'N{row_count}', bom_value.sap_long_text, plain_style)
                worksheet.write(f'O{row_count}', "", only_border_style)
                worksheet.write(f'P{row_count}', "EA - each", plain_style)
                worksheet.write(f'Q{row_count}', "RTIO", plain_style)
                worksheet.write(f'R{row_count}', bom_value.rio_code, plain_style)
                worksheet.write(f'S{row_count}', "No", only_border_style)
                worksheet.write(f'T{row_count}', "", only_border_style)
                worksheet.write(f'U{row_count}', "", only_border_style)
                worksheet.write(f'V{row_count}', "", only_border_style)
                worksheet.write(f'W{row_count}', "", only_border_style)
                worksheet.write(f'X{row_count}', "", only_border_style)
                worksheet.write(f'Y{row_count}', bom_value.detail_drawing, plain_style)
                worksheet.write(f'Z{row_count}', "RTIO", plain_style)
                worksheet.write(f'AA{row_count}', "", only_border_style)
                worksheet.write(f'AB{row_count}', "", only_border_style)
                worksheet.write(f'AC{row_count}', "", only_border_style)
                worksheet.write(f'AD{row_count}', "", only_border_style)
                worksheet.write(f'AE{row_count}', "", only_border_style)
                worksheet.write(f'AF{row_count}', "", only_border_style)
                worksheet.write(f'AG{row_count}', "", only_border_style)
                worksheet.write(f'AH{row_count}', "", only_border_style)
                worksheet.write(f'AI{row_count}', "", only_border_style)
                worksheet.write(f'AJ{row_count}', "", only_border_style)
                worksheet.write(f'AK{row_count}', "", only_border_style)
                worksheet.write(f'AL{row_count}', "", only_border_style)
                worksheet.write(f'AM{row_count}', "", only_border_style)
                worksheet.write(f'AN{row_count}', "", only_border_style)
                worksheet.write(f'AO{row_count}', "", only_border_style)
                worksheet.write(f'AP{row_count}', "", only_border_style)
                worksheet.write(f'AQ{row_count}', "", only_border_style)
                worksheet.write(f'AR{row_count}', "", only_border_style)
                worksheet.write(f'AS{row_count}', "", only_border_style)
                worksheet.write(f'AT{row_count}', "", only_border_style)
                worksheet.write(f'AU{row_count}', "", only_border_style)
                row_count += 1

        except Exception as e:
            _logger.info(e)
            return []
        workbook.close()
        output.seek(0)
        return base64.b64encode(output.getvalue())
