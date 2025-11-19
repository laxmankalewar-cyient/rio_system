/* Copyright 2018 Simone Orsi - Camptocamp SA
License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html). */

odoo.define("rio_cyeims", function (require) {
    "use strict";
    var basic_fields = require("web.basic_fields");

    basic_fields.UrlWidget.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            // Retrieve customized `<a />` text from a field
            // via `text_field` attribute or `options.text_field`
            this.text_field = this.attrs.text_field || this.attrs.options.text_field;
        },
        /**
         * Retrieve anchor text based on options.
         * @returns {String}
         */
        _get_text: function () {
            if (this.text_field) {
                var field_value = this.recordData[this.text_field];
                if (_.isObject(field_value) && _.has(field_value.data)) {
                    field_value = field_value.data.display_name;
                }
                return field_value;
            }
            return this.attrs.text;
        },
        /**
         *
         * @override
         * @private
         */
        _renderReadonly: function () {
            this.attrs.text = this._get_text();
            this._super.apply(this, arguments);
            var field_name = this.attrs.name

            if (field_name === 'dwg_linerdetail' || field_name === 'dwg_markingplan'
             || field_name === 'layout_drawing_no' || field_name === 'detail_drawing'
              || field_name === 'layout_drawings' || field_name === 'detail_drawings') {
                 if (this.value === "NA") {
                    this.$el.text(this.value); // Display plain text, no link
                    return;
                }
                var prefix = 'https://rtio-alim/alimweb/Search/QuickLink.aspx?n='+this.value+'&t=3&d=Main%5cRio_Tinto_EDM&sc=RTIO&state=LatestApproved&cno=RENDITION&m=l'
                this.$el.html(
                    $(this.$el.html()).attr("href", prefix)
                );
                this.$el.html(
                    $(this.$el.html()).addClass("my-url")
                );
            }else{
                this.$el.html(

                    $(this.$el.html()).attr("href", this.value)

                );
            }
        },
    });
});
odoo.define('rio_cyiems.tree_view_extend', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');
    var core = require('web.core');
    var _t = core._t;

    ListRenderer.include({
        _onCellClick: function (event) {
            this._super.apply(this, arguments);
            var self = this;
            var $target = $(event.target);
            if ($target.is('td.rtio_multiple_mtr_class')) {
                this._onclick_rtio_multiple_mtr_class(event);
            }
        },


        _onclick_rtio_multiple_mtr_class: function (event) {
            // Your custom JavaScript function logic here
            event.stopPropagation();

            var $td = $(event.currentTarget);
            var $tr = $td.parent();
            var rowIndex = $tr.prop('rowIndex') - 1;
            var recordID = this._getRecordID(rowIndex);
            var record = this._getRecord(recordID);
            var site_id = parseInt(record.data.site.data.id)
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action({
                name: _t('Rio Code with Multiple Materials'),
                type: 'ir.actions.act_window',
                res_model: 'product.liner_taxonomy',
                view_mode: 'tree,form',
                views: [[false, 'list'],[false, 'form']],
                target: 'current',
                context: {
                    'action' : 'rtio_multiple_mtr',
                    'params':{'site_id':site_id},
                }
            }, options);
        },
    });
});
