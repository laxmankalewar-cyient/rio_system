from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
import re
import os

from odoo.exceptions import ValidationError
from random import randint
import shutil
import secrets
import string
import base64

import logging

_logger = logging.getLogger(__name__)


class DMSDirectory(models.Model):
    _inherit = "dms.directory"

    def _get_default_workflow_id(self):
        return self.env["workflow.stage"].search(
            [('system_stage', '=', True), ('active', '=', False)], limit=1).id


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _compute_checksum(self, bin_data):
        if self.env.context.get("duplicate_content", True):
            return self.env['dms.file'].generate_unique_string()
        return super()._compute_checksum(bin_data)


class DMSFile(models.Model):
    _inherit = "dms.file"

    def replace_file(self, src_path, dest_path):
        try:
            # Extract the base file name from the destination path
            dest_base = os.path.basename(dest_path)

            # Construct the full path for the new replacement file
            new_dest_path = os.path.join(os.path.dirname(dest_path), dest_base)

            # Use shutil.move to replace the file, preserving metadata
            shutil.move(src_path, new_dest_path)  # Replaces and handles potential overwrite

            print(f"File replaced successfully: {src_path} -> {new_dest_path}")

        except FileNotFoundError:
            print(f"Error: Source file '{src_path}' not found.")
        except OSError as e:
            print(f"Error replacing file: {e}")

    def generate_unique_string(self, length=40):
        characters = string.ascii_lowercase + string.digits
        unique_string = ''.join(secrets.choice(characters) for _ in range(length))

        # Use a set to ensure uniqueness (highly likely even without this check)
        seen = set()
        while unique_string in seen:
            unique_string = ''.join(secrets.choice(characters) for _ in range(length))
            seen.add(unique_string)
        _logger.info(f"Unique Checksum for the file: {unique_string}")
        return unique_string

    def create_dms_document_from_file_folder(self, vals):
        file_folder = vals.get("file_folder", False)
        directory_id = vals.get("directory_id", False)

        if not file_folder:
            _logger.info("file foldr is not provided!")
            return
        all_files = self.get_all_file_paths_with_name(file_folder)
        for file_meta in all_files:
            file_name, file_path = file_meta
            v = {"file_path": file_path, "directory_id": directory_id,
                 "name": file_name}
            self.create_dms_file(v)

    def create_dms_file(self, vals):
        if vals.get('file_path', False):
            file = vals.get('file_path', False)
            with open(file, "rb") as file:
                binary_content = file.read()
        else:
            binary_content = vals.get("binary_content", None)
        content = base64.b64encode(binary_content)
        ret = self.env['dms.file'].sudo().search([("directory_id", "=", vals["directory_id"]),
                                                  ("name", "=", vals["name"])])
        if ret:
            dms_id = ret[0]
            dms_id.write({"content": content})
        else:
            vals = {"content": content,
                    "directory_id": vals["directory_id"], "name": vals["name"]}
            dms_id = self.env['dms.file'].sudo().create(vals)
        dms_id._cr.commit()
        return dms_id

    def create_duplicate(self, vals):
        file_path = self.get_dms_file_path()
        temp_file_path = self.copy_file_to_temp_dir(file_path, vals["name"])
        with open(temp_file_path, 'rb') as f:
            content = f.read()
        vals["content"] = content
        ret = self.env['dms.file'].sudo().search([("directory_id", "=", vals["directory_id"]),
                                                  ("name", "=", vals["name"])])
        if ret:
            dms_id = ret[0]
        else:
            dms_id = self.env['dms.file'].sudo().with_context({
                'duplicate_content': True,
            }).create(vals)
            dms_id._cr.commit()
        self.replace_file(temp_file_path, dms_id.get_dms_file_path())
        return dms_id

    def copy_file_to_temp_dir(self, source_file, new_file_name):
        destination_directory = self.get_dms_temp_dir()
        destination_file = os.path.join(destination_directory,
                                        new_file_name if new_file_name else os.path.basename(source_file))
        shutil.copy(source_file, destination_file)
        return destination_file

    def get_dms_temp_dir(self):
        data_dir = tools.config['data_dir']
        db_name = tools.config['db_name']
        filestore_name = 'filestore'

        temp_dir = data_dir + '/' + filestore_name + '/' + db_name + '/' + 'dms_temp_files/'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        return temp_dir

    def get_all_file_paths_with_name(self, folder_path):
        result = []
        for dirpath, dirnames, filenames in os.walk(folder_path):
            result.extend([(filename, os.path.join(dirpath, filename)) for filename in filenames])
        return result or []

    def get_all_file_paths(self, folder_path):
        result = []
        for dirpath, dirnames, filenames in os.walk(folder_path):
            result.extend([os.path.join(dirpath, filename) for filename in filenames])
        return result or []

    def get_dms_file_path(self):
        attachment = self.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'dms.file'), ('res_id', '=', self.id), ('res_field', '=', 'content_file'),
             ('type', '=', 'binary')])
        if not attachment:
            print(f"template file {self.name} not found/not accessible to this user:{self.env.user.name}")
            return None

        fname = attachment.store_fname
        full_path = attachment._full_path(fname)
        return full_path

    def _generate_file_sequence(self, vals):
        if vals.get('file_sequence', _('New')) == _('New'):
            dms_category = vals.get('category_id', False)
            sr_no = False
            if dms_category:
                dms_category = self.env['dms.category'].browse(dms_category)
                if dms_category.sequence_identifier:
                    sr_no = self.env['ir.sequence'].next_by_code(dms_category.sequence_identifier)
            if not sr_no:
                sr_no = self.env['ir.sequence'].next_by_code('dms.file.default')
            if sr_no:
                vals['file_sequence'] = sr_no


DMSFile()
