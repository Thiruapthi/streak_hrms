
frappe.ui.form.on("Job Applicant", {
    refresh: function(frm) {
        var interviewButton = $(".document-link[data-doctype='Interview'] button[data-doctype='Interview']");
        interviewButton.remove();
    },
    before_save(frm) {
        console.log("hello")
		frm.set_value("status", "Interview Pending");
	}
    
});