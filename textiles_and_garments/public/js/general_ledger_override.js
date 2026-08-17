// Override General Ledger Report filters to exclude Employee party type for restricted users

frappe.provide("textiles_and_garments.overrides");

// Configuration: Define restricted and unrestricted roles
const RESTRICTED_ROLES = ["Accounts User", "Sales User"];
const UNRESTRICTED_ROLES = ["Accounts Manager", "System Manager", "HR Manager"];

function is_user_restricted() {
    // Check if current user is restricted
    const user = frappe.session.user;
    const user_roles = frappe.user_roles || [];
    
    // Administrator is never restricted
    if (user === "Administrator") {
        return false;
    }
    
    // Check if user has any unrestricted role
    for (let role of UNRESTRICTED_ROLES) {
        if (user_roles.includes(role)) {
            return false;
        }
    }
    
    // Check if user has any restricted role
    for (let role of RESTRICTED_ROLES) {
        if (user_roles.includes(role)) {
            return true;
        }
    }
    
    // Default: not restricted
    return false;
}

textiles_and_garments.overrides.general_ledger = function() {
    // Only apply restriction if user is restricted
    if (!is_user_restricted()) {
        console.log("User is not restricted - Employee option will be available");
        return;
    }
    
    console.log("User is restricted - Removing Employee from Party Type options");
    
    // Store original onload if exists
    const original_onload = frappe.query_reports["General Ledger"] 
        ? frappe.query_reports["General Ledger"].onload 
        : null;

    // Get all filters
    let filters = frappe.query_reports["General Ledger"].filters;
    
    // Find and modify party_type filter
    for (let i = 0; i < filters.length; i++) {
        if (filters[i].fieldname === "party_type") {
            // Override the options to exclude Employee for restricted users
            filters[i].options = Object.keys(frappe.boot.party_account_types || {})
                .filter(party_type => party_type !== "Employee");
            break;
        }
    }

    // Add custom onload
    frappe.query_reports["General Ledger"].onload = function(report) {
        // Call original onload if it existed
        if (original_onload) {
            original_onload(report);
        }
        
        // Add info button for restricted users
        report.page.add_inner_button(__('Access Info'), function() {
            frappe.msgprint({
                title: __('Employee Data Restricted'),
                indicator: 'orange',
                message: __('Employee party type is restricted for your role. Please contact your administrator if you need access to employee transactions.')
            });
        });
    };
};

// Execute override when document is ready
$(document).on('page-change', function() {
    if (frappe.get_route()[0] === 'query-report' && frappe.get_route()[1] === 'General Ledger') {
        setTimeout(function() {
            textiles_and_garments.overrides.general_ledger();
        }, 500);
    }
});

// Also execute on page load
// frappe.ready(function() {
//     if (frappe.get_route()[0] === 'query-report' && frappe.get_route()[1] === 'General Ledger') {
//         textiles_and_garments.overrides.general_ledger();
//     }
// });

$(document).ready(function() {
    // Run on initial page load
    if (frappe.get_route()[0] === 'query-report' && frappe.get_route()[1] === 'General Ledger') {
        textiles_and_garments.overrides.general_ledger();
    }

    // Re-run on route change
    frappe.router.on('change', function() {
        if (frappe.get_route()[0] === 'query-report' && frappe.get_route()[1] === 'General Ledger') {
            textiles_and_garments.overrides.general_ledger();
        }
    });
});

