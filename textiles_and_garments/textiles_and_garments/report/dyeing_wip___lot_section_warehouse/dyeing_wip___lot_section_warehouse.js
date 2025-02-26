// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["Dyeing WIP - Lot Section Warehouse"] = {
    "filters": [],

    onload: function(report) {
        frappe.call({
            method: "textiles_and_garments.textiles_and_garments.report.dyeing_wip___lot_section_warehouse.dyeing_wip___lot_section_warehouse.get_data",  // Update with your actual method path
            args: {
                filters: {}  // Pass any required filters here
            },
            callback: function(response) {
                console.log("Dyeing WIP Data:", response.message);
            }
        });
    }
};

