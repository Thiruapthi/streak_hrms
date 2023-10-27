frappe.ui.form.on('Leave Application', {
    refresh: function(frm) {  
        frm.page.wrapper.find('.report-link').on('click', function() {
            var selectedEmployee = cur_frm.doc.employee;
            var employeeCompany = cur_frm.doc.company;
            if (selectedEmployee) { 
                frappe.set_route("query-report", "Employee Leave Balance", {
                    "employee": selectedEmployee,
                    "company":employeeCompany
                });
            } 
        });
    }
});
