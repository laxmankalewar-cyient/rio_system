odoo.define("rio_cyeims.dashboard", function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');
    var web_client = require('web.web_client');
    var _t = core._t;
    var framework = require('web.framework');
    var session = require('web.session');
    var operation_types;
    var result_2;
    var result_3;
    var DashBoard = AbstractAction.extend({
        contentTemplate: 'Dashboard',
        events: {
        'click #sap_mtr_with_new_mtr_required_info': 'onclick_flocs_identified_new_mtr_required_info',
        'click #flocs_identified_and_det_drw_not_identified_info': 'onclick_flocs_identified_and_det_drw_not_identified_info',
        'click .onclick_multi_liner': 'onclick_multi_liner',
        'click .dwg_linerdetails':'onclick_dwg_linerdetails',
        'click #unique_liner_info': 'onclick_unique_liner_info',
        'click #duplicate_materials_info': 'onclick_duplicate_materials_info',
        'click #show_all_sites': 'onclick_show_all_sites',
        'click #apply_sites_filter': 'onclick_apply_sites_filter',
        'click .unique-liner-trigger': 'toggle_unique_liner_details',
        'click .repeated-liner-trigger': 'toggle_repeated_liner_details',
        'click #new_existing_material_info': 'onclick_new_existing_material_info',
        'click #new_material_created_and_required_info': 'onclick_new_material_created_and_required_info',
        'click .onclick_same_riocode_mtr_na': 'onclick_same_riocode_mtr_na',
        'click .onclick_riocode_repeated_multitime_same_material': 'onclick_riocode_repeated_multitime_same_material',
        'click .onclick_riocode_multiple_material_without_na': 'onclick_riocode_multiple_material_without_na',
        'click .onclick_riocode_multiple_material_with_na': 'onclick_riocode_multiple_material_with_na',
        },

        init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['SiteTiles','SiteWithUniqueLiner'];
        },

        willStart: function() {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function() {
                return ;
            });
        },

        start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.render_dashboards();
                self.render_graphs();
                self.$el.parent().addClass('oe_background_grey');
            });
        },

        render_dashboards: function() {
            var self = this;
                _.each(this.dashboards_templates, function(template) {
                    self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}));
                });
        },
        render_graphs: function(){
            var self = this;
            self.rio_render_operation_tile();
            self.sap_mtr_with_new_mtr_required();
            self.flocs_identified_and_det_drw_not_identified();
            self.duplicate_materials_liners();
            self.rio_render_top_bar_graph();
            self.canvas_existing_material();
            self.new_material_created_and_required();
            self.render_all_sites();
        },

        render_all_sites: function() {
            console.log('Logged-in User ID:', session.uid);
            rpc.query({
                model: "rio.site_dashboard",
                method: "get_all_sites",
                args: [session.uid]
            }).then(function (result) {
                result.forEach((obj, index) => {
                    console.log(obj.site_name);
                    if (obj.is_selected) {
                        $('#site_table').append('<tr><td>'+obj.site_name+'</td><td><input type="checkbox" checked value="'+obj.site_id+'" /></td></tr>')
                    }else{
                        $('#site_table').append('<tr><td>'+obj.site_name+'</td><td><input type="checkbox" value="'+obj.site_id+'"/></td></tr>')
                    }

                });
                $('#site_table').append('<tr><td><button class="btn btn-info" id="show_all_sites"> <i class="fa fa-close"></i> Cancel </button></td><td><button class="btn btn-info" id="apply_sites_filter"> <i class="fa fa-refresh"></i> Apply Filter </button></td></tr>')
            });

        },
        toggle_unique_liner_details: function(event) {
            const $trigger = this.$(event.currentTarget);
            const $details = $trigger.next('.unique-liner-details');
            $details.toggle();
        },
        toggle_repeated_liner_details:function(event) {
            const $trigger = this.$(event.currentTarget);
            const $details = $trigger.next('.repeated-liner-details');
            $details.toggle();
        },

        rio_render_operation_tile: function() {
            var self = this;
            var def1 =  this._rpc({
                model: 'rio.site_dashboard',
                method: 'get_site_details'
            }).then(function(result) {
                var g = 0;
                Object.entries(result).forEach(([key, value]) => {
                    result_2 = value;
                    var site_id = result_2[1].replace(/\s+/g, '_').toLowerCase().concat("_",result_2[0].toString());
                    const colors = ["red","orange","purple","steel","rebecca","brown","pink","grey","black"];
                    var html = '
                    <div class="col-sm-12 col-md-6 col-lg-3">
                    <div class="dashboard-card dashboard-card--border-top dashboard-card--border-top-' + colors[g] +  '" style="background-color: azure;">
                    <div class="dashboard-card__details"><span class="dashboard-card__title">' + result_2[1]+ '</span>
                    <span class="count-container">' + result_2[2] +  '</span>
                    </div>
                    <ul class="dashboard-card__stats">
                    <li class="dashboard-card__stat_late unique-liner-trigger">
                    <div class="popup-wrapper">
                        <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                        <div class="dashboard-card__stat-title_late">Unique Liner</div>
                        <div class="popup-text">Unique Liner Specs split up by below:</div>
                        <div class="dashboard-card__stat-count_late">' + result_2[3]+ '</div>
                        <div class="dropdown-toggle ms-2 unique-liner-btn" data-bs-toggle="dropdown" aria-expanded="false" role="button">
                            <i class="fas fa-chevron-down"></i>
                        </div>
                        </div>
                        </div>
                    </li>
                    <div class="unique-liner-details" style="display: none;">

                        <li class="dashboard-card__stat_late">
                        <div class="popup-wrapper">
                            <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                            <div class="dashboard-card__stat-title_late" style="font-size: smaller;">&nbsp;&nbsp;Liner with NA</div>
                            <div class="popup-text">Unique liner specs not matched to either existing SAP material number or newly created material number (to be catalogued)</div>
                            <div class="dashboard-card__stat-count_late">' + result_2[7]+ '</div>
                            </div>
                            </div>
                        </li>
                        <li class="dashboard-card__stat_late">
                        <div class="popup-wrapper">
                            <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                            <div class="dashboard-card__stat-title_late" style="font-size: smaller;">&nbsp;&nbsp;Liner with Material</div>
                            <div class="popup-text">Unique liner spec matching to existing or newly created SAP material number</div>
                            <div class="dashboard-card__stat-count_late">' + result_2[8]+ '</div>
                            </div>
                            </div>
                        </li>
                    </div>

                    '
                    if (result_2[9]) {
                    html += '
                        <li class="dashboard-card__stat_late repeated-liner-trigger">
                        <div class="popup-wrapper">
                            <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                            <div class="dashboard-card__stat-title_late">Repeated Liners</div>
                            <div class="popup-text">Identical liner specs repeated across multiple FLOCs or sites split up by below:</div>
                            <div class="dashboard-card__stat-count_late">' + result_2[4]+ '</div>
                                <div class="dropdown-toggle ms-2 repeated-liner-btn" data-bs-toggle="dropdown" aria-expanded="false" role="button">
                                    <i class="fas fa-chevron-down"></i>
                                </div>
                            </div>
                            </div>
                        </li>
                        <div class="repeated-liner-details" style="display: none;">
                            <li class="dashboard-card__stat_late onclick_same_riocode_mtr_na" id="' + site_id + '" style="cursor: pointer;">
                            <div class="popup-wrapper">
                                <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                                <div class="dashboard-card__stat-title_late" style="cursor: pointer; color: #1f12e9; font-weight: bold;font-size: smaller;">&nbsp;&nbsp;Same riocode with Material No. & NA</div>
                                <div class="popup-text">Identical liner spec matched to SAP material number but liners with NA still to be confirmed by site if a true match </div>
                                <div class="dashboard-card__stat-count_late">' + result_2[10]+ '</div>
                                </div>
                                </div>
                            </li>
                            <li class="dashboard-card__stat_late onclick_riocode_repeated_multitime_same_material" id="' + site_id + '" style="cursor: pointer;">
                            <div class="popup-wrapper">
                                <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                                <div class="dashboard-card__stat-title_late" style="cursor: pointer; color: #1f12e9; font-weight: bold;font-size: smaller;">&nbsp;&nbsp;Riocode repeated multi times with same material</div>
                                <div class="popup-text">Identical liner spec matching existing or newly created SAP material number used across multiple FLOCs or sites</div>
                                <div class="dashboard-card__stat-count_late">' + result_2[11]+ '</div>
                                </div>
                                </div>
                            </li>
                            <li class="dashboard-card__stat_late onclick_riocode_multiple_material_without_na" id="' + site_id + '" style="cursor: pointer;">
                            <div class="popup-wrapper">
                                <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                                <div class="dashboard-card__stat-title_late" style="cursor: pointer; color: #1f12e9; font-weight: bold;font-size: smaller;">&nbsp;&nbsp;Same Riocode with multi mat without NA</div>
                                <div class="popup-text">Identical liner spec matched to multiple existing SAP material numbers (duplicates)</div>
                                <div class="dashboard-card__stat-count_late">' + result_2[12]+ '</div>
                                </div>
                                </div>
                            </li>
                            <li class="dashboard-card__stat_late onclick_riocode_multiple_material_with_na" id="' + site_id + '" style="cursor: pointer;">
                            <div class="popup-wrapper">
                                <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                                <div class="dashboard-card__stat-title_late" style="cursor: pointer; color: #1f12e9; font-weight: bold;font-size: smaller;">&nbsp;&nbsp;Riocode repeated multi times with NA</div>
                                <div class="popup-text">Identical liner specs used across multiple FLOCs or sites not matched to existing SAP material number (to be catalogued)</div>
                                <div class="dashboard-card__stat-count_late">' + result_2[13]+ '</div>
                                </div>
                                </div>
                            </li>
                        </div>'
                    }else{
                    html += '
                        <li class="dashboard-card__stat_late">
                        <div class="popup-wrapper">
                            <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                            <div class="dashboard-card__stat-title_late">Repeated Liners</div>
                            <div class="popup-text">Identical liner specs repeated across multiple FLOCs or sites split up</div>
                            <div class="dashboard-card__stat-count_late">' + result_2[4]+ '</div>
                            </div>
                            </div>
                        </li>'
                    }
                    html += '<li class="dashboard-card__stat_late">
                    <div class="popup-wrapper">
                        <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                        <div class="dashboard-card__stat-title_late">FLOCs Identified</div>
                        <div class="popup-text">Count of FLOCs with drawings identified in taxonomy </div>
                        <div class="dashboard-card__stat-count_late">' + result_2[5]+ '</div>
                        </div>
                        </div>
                    </li>
                    <li class="dashboard-card__stat_late onclick_multi_liner" id="' + site_id +  '" style="cursor: pointer;">
                        <div class="popup-wrapper">
                        <a>
                            <div class="d-flex justify-content-between align-items-center text-dark text-decoration-none">
                            <div class="dashboard-card__stat-title_late" style="cursor: pointer; color: #1f12e9; font-weight: bold" >Multiple Materials</div>
                            <div class="popup-text">Count of identical liners specs matched to multiple SAP material numbers (unique count of duplicate liner specs) </div>
                            <div class="dashboard-card__stat-count_late" style="color: #1f12e9; font-weight: bold">' + result_2[6]+ '</div>
                            </div>
                        </a>
                        </div>
                    </li>
                    </ul>
                    </div></div>'
                    $('#set').append(html)
                    g++;
                });

            });
        },

    new_material_created_and_required: function () {
            var self = this;
            var chartInstance = null;
            self.$('#new_material_created_and_required_table').hide();
            rpc.query({
                model: "rio.site_dashboard",
                method: "get_new_material_created_and_required",
                args: []
            }).then(function (result) {
                const ctx = self.$("#new_material_created_and_required_table_canvaspie").get(0).getContext("2d");
                const $selector = self.$("#materialsiteSelector");
                const $table = self.$("#new_material_created_and_required_table");

                $selector.empty();
                $selector.append(`<option value="all">All Sites</option>`);
                for (let i = 0; i < result.name.length; i++) {
                    $selector.append(`<option value="${i}">${result.name[i]}</option>`);
                }
                $table.find("tr:gt(0)").remove(); // Clear existing rows (keep header)
                for (let i = 0; i < result.name.length; i++) {
                    const siteName = result.name[i];
                    const created = result.new_material_created[i] || 0;
                    const required = result.new_material_creation_required[i] || 0;
                    $table.append(`
                        <tr>
                            <td>${siteName}</td>
                            <td>${created}</td>
                            <td>${required}</td>
                        </tr>
                    `);
                }

                function updateChart(selectedIndex) {
                    let created = 0;
                    let required = 0;
                    if (selectedIndex === "all") {
                        created = result.new_material_created.reduce((sum, val) => sum + val, 0);
                        required = result.new_material_creation_required.reduce((sum, val) => sum + val, 0);
                    } else {
                        const i = parseInt(selectedIndex);
                        created = result.new_material_created[i];
                        required = result.new_material_creation_required[i];
                    }
                    const data = created === 0 && required === 0 ? [1, 1] : [created, required];

                    if (chartInstance) {
                        chartInstance.destroy();
                    }

                    chartInstance = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: ['New Materials Created', 'New Material Creation Required'],
                            datasets: [{
                                data: data,
                                backgroundColor: ['#FFEB3B', '#4CAF50'],
                                borderColor: ['#ffffff', '#ffffff'],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: {
                                legend: {
                                    position: 'top'
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function (context) {
                                            const value = context.parsed;
                                            const total = context.chart._metasets[0].total;
                                            const percentage = ((value / total) * 100).toFixed(1) + '%';
                                            return `${context.label}: ${value} (${percentage})`;
                                        }
                                    }
                                }
                            }
                        }
                    });
                }

                updateChart("all");
                $selector.off("change").on("change", function () {
                    updateChart(this.value);
                });
            });
    },

    //    top ten bar graph
    flocs_identified_and_det_drw_not_identified: function () {
            var self = this;
            var chartInstance = null;
            rpc.query({
                model: "rio.site_dashboard",
                method: "get_sites_with_flocs_identified_and_det_drw_not_identified",
            }).then(function (result) {
                var sites = result[0];     // Site names
                var count_1 = result[1];   // FLOCs Identified
                var count_2 = result[2];   // FLOCs Not Identified
                let $selector = $('#siteSelector');
                $selector.empty();
                for (let i = 0; i < sites.length; i++) {
                    $selector.append(`<option value="${i}">${sites[i]}</option>`);
                }
                function updateDisplay(selectedIndex) {
                    $('#flocs_identified_and_det_drw_not_identified_table').hide();
                    $('#flocs_identified_and_det_drw_not_identified_table tr:not(:first)').remove();

                    let displaySites = [];
                    let displayIdentified = [];
                    let displayNotIdentified = [];
                    if (selectedIndex === "all") {
                        displaySites = sites;
                        displayIdentified = count_1;
                        displayNotIdentified = count_2;
                    } else {
                        let i = parseInt(selectedIndex);
                        displaySites = [sites[i]];
                        displayIdentified = [count_1[i]];
                        displayNotIdentified = [count_2[i]];
                    }
                   for (let i = 0; i < displaySites.length; i++) {
                        $('#flocs_identified_and_det_drw_not_identified_table').append(`
                            <tr>
                            <td>${displaySites[i]}</td>
                            <td>${displayIdentified[i]}</td>
                            <td>${displayNotIdentified[i]}</td>
                            </tr>
                        `);
                    }
                   if (chartInstance) {
                        chartInstance.destroy();
                    }
                   let totalIdentified = displayIdentified.reduce((sum, val) => sum + (isNaN(val) ? 0 : val), 0);
                    let totalNotIdentified = displayNotIdentified.reduce((sum, val) => sum + (isNaN(val) ? 0 : val), 0);
                    let total = totalIdentified + totalNotIdentified;
                    const percentageIdentified = ((totalIdentified / total) * 100).toFixed(2);
                    const percentageNotIdentified = ((totalNotIdentified / total) * 100).toFixed(2);
                    var ctx = self.$("#flocs_identified_and_det_drw_not_identified_canvaspie").get(0).getContext("2d");
                    chartInstance = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: ['FLOCs Identified', 'FLOCs Not Identified'],
                            datasets: [{
                                data: [totalIdentified, totalNotIdentified],
                                backgroundColor: ['#F0AB00', '#3C3D99'],
                                borderColor: ['#ffffff', '#ffffff'],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: {
                                legend: {
                                    position: 'top'
                                },
                                tooltip: {
                                    enabled: false // Disable default tooltip
                                }
                            },
                            hover: {
                            onHover: function (event, chartElement) {
                                    const tooltip = document.getElementById('tooltip');
                                    if (chartElement && chartElement.length) {
                                        const index = chartElement[0]._index;
                                        const value = chartInstance.data.datasets[0].data[index];
                                        const label = chartInstance.data.labels[index];
                                        const total = chartInstance.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(2);

                                        tooltip.innerText = `${label}: ${percentage}%`;
                                        tooltip.style.left = (event.clientX + 10) + 'px';
                                        tooltip.style.top = (event.clientY + 10) + 'px';
                                        tooltip.style.display = 'block';
                                    } else {
                                        tooltip.style.display = 'none';
                                }
                            }
                            }
                        }
                    });
                }
                updateDisplay($('#siteSelector').val());
                $selector.off("change").on("change", function () {
                    updateDisplay(this.value);
                });
            });
        },

        sap_mtr_with_new_mtr_required:function(){
            var self = this
            rpc.query({
                model: "rio.site_dashboard",
                method: "get_sites_sap_mtr_with_new_mtr_required",
            }).then(function (result) {
                var ctx = self.$("#sap_mtr_with_new_mtr_required_canvas");
                // Define the data
                var sites = result[0] // Add data values to array
                var count_1 = result[1]
                var count_2 = result[2]
                var j = 0
                Object.entries(sites).forEach(([key, value]) => {
                    $('#sap_mtr_with_new_mtr_required_table').append('<tr><td>'+sites[j]+'</td><td>'+count_1[j]+'</td><td>'+count_2[j]+'</td></tr>')
                    j++;
                });
                $('#sap_mtr_with_new_mtr_required_table').hide();
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: sites,//x axis
                        datasets: [
                                {
                                    label: 'SAP Material Identified',
                                    data: count_1,
                                    backgroundColor: '#6d5c16',
                                    borderColor: '#CCCCFF',
                                    borderWidth: 1,
                                    type: 'bar', // Set this data to a line chart
                                    fill: false
                                },
                                {
                                    label: 'New Materials Required',
                                    data: count_2,
                                    backgroundColor: '#a05195',
                                    borderColor: '#a05195',
                                    type: 'bar', // Set this data to a line chart
                                    fill: false

                                }
                                ]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }
                });
            });
        },

        canvas_existing_material: function() {
            var self = this;

            rpc.query({
                model: "rio.site_dashboard",
                method: "get_canvas_existing_material",
            }).then(function (result) {
                var ctx = self.$("#canvas_existing_material");
                var existing_material_status = result.status;
                var count = result.count;

                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: existing_material_status,
                        datasets: [{
                            label: 'Count',
                            data: count,
                            backgroundColor: [
                                "#003f5c", "#f95d6a", "#2f4b7c", "#665191", "#d45087",
                                "#ff7c43", "#ffa600", "#a05195", "#6d5c16", "#CCCCFF"
                            ],
                            borderColor: [
                                "#003f5c", "#f95d6a", "#2f4b7c", "#665191", "#d45087",
                                "#ff7c43", "#ffa600", "#a05195", "#6d5c16", "#CCCCFF"
                            ],
                            barPercentage: 0.5,
                            barThickness: 4,
                            maxBarThickness: 6,
                            minBarLength: 0,
                            borderWidth: 0.5,
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                }
                            }],
                            xAxes: [{
                                ticks: {
                                    display: false
                                },
                                gridLines: {
                                    drawTicks: false
                                },
                                scaleLabel: {
                                    display: false
                                }
                            }]
                        }
                    }
                });
            });
        },

    duplicate_materials_liners:function(){
            var self = this
            rpc.query({
                model: "rio.site_dashboard",
                method: "get_duplicate_materials",
            }).then(function (result) {
                var ctx = self.$("#duplicate_materials_canvaspie");
                var sites = result.name // Add data values to array
                var count = result.count;
                var j = 0
                Object.entries(result.count).forEach(([key, value]) => {
                    $('#duplicate_materials_table').append('<tr><td>'+sites[j]+'</td><td>'+value+'</td></tr>')
                    j++;
                });
                $('#duplicate_materials_table').hide();
                var duplicateMaterialsChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: sites,//x axis
                        datasets: [{
                            label: 'Count', // Name the series
                            data: count, // Specify the data values array
                            backgroundColor: [
                                "#003f5c",
                                "#f95d6a",
                                "#2f4b7c",
                                "#665191",
                                "#d45087",
                                "#ff7c43",
                                "#ffa600",
                                "#a05195",
                                "#6d5c16",
                                "#CCCCFF"

                            ],
                            borderColor: [
                                "#003f5c",
                                "#f95d6a",
                                "#2f4b7c",
                                "#665191",
                                "#d45087",
                                "#ff7c43",
                                "#ffa600",
                                "#a05195",
                                "#6d5c16",
                                "#CCCCFF"
                            ],

                            barPercentage: 0.5,
                            barThickness: 4,
                            maxBarThickness: 6,
                            minBarLength: 0,
                            borderWidth: 0.5, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
//                        onClick: event => {
//                            const res = duplicateMaterialsChart.getElementsAtEventForMode(
//                                    event,
//                                    'nearest',
//                                    { intersect: true },
//                                    true
//                                  );
//                                  // If didn't click on a bar, `res` will be an empty array
//                                  if (res.length === 0) {
//                                    return;
//                                  }
//                                  // Alerts "You clicked on A" if you click the "A" chart
//                                  alert('You clicked on ' + duplicateMaterialsChart.data.labels[res[0]._index]);
//                        }

                    }//                                borderColor: '#66aecf',
                });
            });
        },

    rio_render_top_bar_graph:function(){
            var self = this
            rpc.query({
                model: "rio.site_dashboard",
                method: "get_site_with_unique_liner",
            }).then(function (result) {
                var ctx = self.$("#canvaspie");
                var sites = result.sites // Add data values to array
                var count = result.count;
                var j = 0
                Object.entries(result.count).forEach(([key, value]) => {
                    $('#unique_liner_table').append('<tr><td>'+sites[j]+'</td><td>'+value+'</td></tr>')
                    j++;
                });
                $('#unique_liner_table').hide();
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: sites,//x axis
                        datasets: [{
                            label: 'Count', // Name the series
                            data: count, // Specify the data values array
                            backgroundColor: [
                                "#003f5c",
                                "#f95d6a",
                                "#2f4b7c",
                                "#665191",
                                "#d45087",
                                "#ff7c43",
                                "#ffa600",
                                "#a05195",
                                "#6d5c16",
                                "#CCCCFF"

                            ],
                            borderColor: [
                                "#003f5c",
                                "#f95d6a",
                                "#2f4b7c",
                                "#665191",
                                "#d45087",
                                "#ff7c43",
                                "#ffa600",
                                "#a05195",
                                "#6d5c16",
                                "#CCCCFF"
                            ],

                            barPercentage: 0.5,
                            barThickness: 4,
                            maxBarThickness: 6,
                            minBarLength: 0,
                            borderWidth: 0.5, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }//                                borderColor: '#66aecf',
                });
            });
        },

        onclick_flocs_identified_new_mtr_required_info: function(f) {
            var x = document.getElementById("sap_mtr_with_new_mtr_required_table");
            if (x.style.display === "none") {
                x.style.display = "block";
              } else {
                x.style.display = "none";
            }
        },

        onclick_apply_sites_filter: function(f) {
            const table = document.getElementById("site_table");
            var x = document.getElementById("site_table_container");
            x.style.display = "none";
            const checkboxes = table.querySelectorAll("input[type='checkbox']");
            let selectedValues = [];
            checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    selectedValues.push(checkbox.value);
                }
            });
            rpc.query({
                model: "rio.site_dashboard",
                method: "save_filter_sites",
                args: [session.uid,selectedValues]
            }).then(function (result) {
                location.reload();
             });
        },

        onclick_show_all_sites: function(f) {
            var x = document.getElementById("site_table_container");
            if (x.style.display === "none") {
                x.style.display = "block";
              } else {
                x.style.display = "none";
            }
        },

        onclick_flocs_identified_and_det_drw_not_identified_info: function(f) {
            var x = document.getElementById("flocs_identified_and_det_drw_not_identified_table");
            if (x.style.display === "none") {
                x.style.display = "block";
              } else {
                x.style.display = "none";
            }
        },

        onclick_multi_liner: function(f) {
            var id = this.$(f.currentTarget).attr('id');
            const pieces = id.split("_")
            const site_id = parseInt(pieces[pieces.length - 1])
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

        onclick_unique_liner_info: function(f) {
            var x = document.getElementById("unique_liner_table");
            if (x.style.display === "none") {
                x.style.display = "block";
              } else {
                x.style.display = "none";
            }
        },
        onclick_new_existing_material_info: function(f) {
            var x = document.getElementById("new_existing_material_table");
            if (x.style.display === "none") {
                x.style.display = "block";
              } else {
                x.style.display = "none";
            }
        },

        onclick_duplicate_materials_info: function(f) {
            var x = document.getElementById("duplicate_materials_table");
            if (x.style.display === "none") {
                x.style.display = "block";
              } else {
                x.style.display = "none";
            }
        },

        onclick_new_material_created_and_required_info: function(f) {
            var x = document.getElementById("new_material_created_and_required_table");
            if (x.style.display === "none") {
                x.style.display = "block";
              } else {
                x.style.display = "none";
            }
        },

        onclick_same_riocode_mtr_na: function(f) {
        this.open_repeated_liner_filter_view(f, {
            name: 'Same RIO-Code with NA Materials',
            context_flag: 'search_rtio_liner_code_greater_one',
            domain_field: 'rtio_liner_code_greater_one',
            domain_value: 'Same RIO-Code With NA',
        });
    },

    onclick_riocode_repeated_multitime_same_material: function(f) {
        this.open_repeated_liner_filter_view(f, {
            name: 'Riocode repeated multi times with same material',
            context_flag: 'search_rtiocode_repeated_multitime_same_material',
            domain_field: 'rtiocode_repeated_multitime_same_material',
            domain_value: 'Riocode repeated multi same material',
        });
    },

    onclick_riocode_multiple_material_without_na: function(f) {
        this.open_repeated_liner_filter_view(f, {
            name: 'Same riocode with multiple mat without NA',
            context_flag: 'search_multiple_material_without_na_rcode',
            domain_field: 'multiple_material_without_na_rcode',
            domain_value: 'Riocode with multi Material without NA',
        });
    },

    onclick_riocode_multiple_material_with_na: function(f) {
        this.open_repeated_liner_filter_view(f, {
            name: 'Same riocode with multiple mat with NA',
            context_flag: 'search_multiple_material_with_na_rcode',
            domain_field: 'multiple_material_with_na_rcode',
            domain_value: 'Riocode with multi Material with NA',
        });
    },

    open_repeated_liner_filter_view: function(f, config) { // filter view for all the filters
        var id = this.$(f.currentTarget).attr('id');
        const pieces = id.split("_");
        const site_id = parseInt(pieces[pieces.length - 1]);

        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb, // if user goes back. then does cleanup
        };

        let context = {
            params: { site_id: site_id },
        };
        context[config.context_flag] = 1;

        this.do_action({
            name: _t(config.name),
            type: 'ir.actions.act_window',
            res_model: 'product.liner_taxonomy',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            context: context,
            domain: [[config.domain_field, '=', config.domain_value]],
        }, options);
        },


    });
    core.action_registry.add('rio_dashboard_tag', DashBoard);
    return;
});
