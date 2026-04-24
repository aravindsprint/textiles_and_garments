// Copyright (c) 2026, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Attendance With Leave Type"] = {
    filters: [
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { value: 1,  label: __("January") },
                { value: 2,  label: __("February") },
                { value: 3,  label: __("March") },
                { value: 4,  label: __("April") },
                { value: 5,  label: __("May") },
                { value: 6,  label: __("June") },
                { value: 7,  label: __("July") },
                { value: 8,  label: __("August") },
                { value: 9,  label: __("September") },
                { value: 10, label: __("October") },
                { value: 11, label: __("November") },
                { value: 12, label: __("December") },
            ],
            default: new Date().getMonth() + 1,
            reqd: 1
        },
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Int",
            default: new Date().getFullYear(),
            reqd: 1
        },
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "department",
            label: __("Department"),
            fieldtype: "Link",
            options: "Department"
            // No default — blank means all departments
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!column.fieldname || !column.fieldname.startsWith("day_") || !data) {
            return value;
        }

        const raw = data[column.fieldname];
        if (!raw) return value;

        // ── Exact match colours ──────────────────────────────────────────
        const colorMap = {
            "P":    { bg: "#d4edda", color: "#155724" },  // green  - Present
            "A":    { bg: "#f8d7da", color: "#721c24" },  // red    - Absent
            "WFH":  { bg: "#d1ecf1", color: "#0c5460" },  // teal   - Work From Home
            "HD/P": { bg: "#fff3cd", color: "#856404" },  // yellow - Half Day Present
        };

        let style = colorMap[raw];

        if (!style) {
            if (raw.startsWith("HD/")) {
                // HD/EL, HD/CL, HD/SL — half day on leave
                style = { bg: "#f0e6ff", color: "#5a1a8a" };  // purple
            } else {
                // Full leave — EL, CL, SL, LWP etc.
                style = { bg: "#e2d9f3", color: "#4a235a" };  // deep purple
            }
        }

        return `<span style="
            background:    ${style.bg};
            color:         ${style.color};
            padding:       2px 5px;
            border-radius: 3px;
            font-weight:   600;
            font-size:     11px;
            display:       inline-block;
            min-width:     32px;
            text-align:    center;
            white-space:   nowrap;
        ">${raw}</span>`;
    },

    onload: function(report) {
        const legend = `
            <div style="
                display:     flex;
                gap:         10px;
                flex-wrap:   wrap;
                padding:     8px 0 4px 0;
                font-size:   12px;
                align-items: center;
            ">
                <b>Legend:</b>
                <span>
                    <span style="background:#d4edda;color:#155724;padding:1px 6px;
                        border-radius:3px;font-weight:600;">P</span>
                    Present
                </span>
                <span>
                    <span style="background:#f8d7da;color:#721c24;padding:1px 6px;
                        border-radius:3px;font-weight:600;">A</span>
                    Absent
                </span>
                <span>
                    <span style="background:#d1ecf1;color:#0c5460;padding:1px 6px;
                        border-radius:3px;font-weight:600;">WFH</span>
                    Work From Home
                </span>
                <span>
                    <span style="background:#fff3cd;color:#856404;padding:1px 6px;
                        border-radius:3px;font-weight:600;">HD/P</span>
                    Half Day Present
                </span>
                <span>
                    <span style="background:#f0e6ff;color:#5a1a8a;padding:1px 6px;
                        border-radius:3px;font-weight:600;">HD/EL</span>
                    Half Day on Leave
                </span>
                <span>
                    <span style="background:#e2d9f3;color:#4a235a;padding:1px 6px;
                        border-radius:3px;font-weight:600;">EL / CL…</span>
                    Full Leave
                </span>
            </div>
        `;
        $(report.wrapper).find(".page-form").append(legend);
    }
};