frappe.ui.form.on('Leave Application', {
    employee:function(frm){
        let employee_id = frm.doc.employee
        frm.set_query("leave_type", function () {
            return {
                query: "hyde_app.role_perms_api.hideing_leave_without_pay",
                filters:{"employee_id":employee_id}
            };
        });
    },
 
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
    },

    leave_approver: function(frm) {
		if (frm.doc.leave_approver) {
            frappe.call({
                method:'hyde_app.api.get_user_details',
                args: {
                    user:frm.doc.leave_approver
                },
                callback: function(r){ 
                    if(r.message){
                        var full_name = r.message[0].full_name
                    	frm.set_value("leave_approver_name", full_name)
                    }
                }
            })
		}
	}
});