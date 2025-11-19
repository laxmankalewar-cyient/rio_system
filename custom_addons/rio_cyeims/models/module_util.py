import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class ModuleUtils(models.Model):
    _name = "module.utils"
    _description = "Utility Class"

    def get_detailed_drawing_link(self, detailed_drawing):
        dwg_linerdetail_html = f"<a href='https://rtio-alim/alimweb/Search/QuickLink.aspx?n={detailed_drawing}&amp;t=3&amp;d=Main%5cRio_Tinto_EDM&amp;sc=RTIO&amp;state=LatestRevision&amp;m=l' target='_blank'>{detailed_drawing}</a>"
        return dwg_linerdetail_html

    def get_marking_plan_link(self, dwg_markingplan):
        dwg_markingplan_html = f"<a href='https://rtio-alim/alimweb/Search/QuickLink.aspx?n={dwg_markingplan}&amp;t=3&amp;d=Main%5cRio_Tinto_EDM&amp;sc=RTIO&amp;state=LatestRevision&amp;m=l' target='_blank'>{dwg_markingplan}</a>"
        return dwg_markingplan_html
