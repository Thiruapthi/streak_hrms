
frappe.ui.form.on("Job Applicant", {
    refresh: function(frm) {
        var interviewButton = $(".document-link[data-doctype='Interview'] button[data-doctype='Interview']");
        interviewButton.remove();
    }
    
});