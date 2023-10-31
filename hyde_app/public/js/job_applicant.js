
frappe.ui.form.on("Job Applicant", {
    refresh: function(frm) {
        var interviewButton = $(".document-link[data-doctype='Interview'] button[data-doctype='Interview']");
        interviewButton.remove();
        const documentTypes = ['Employee', 'Job Offer', 'Employee Onboarding', 'Appointment Letter'];

        documentTypes.forEach((type) => {
            const selector = `.document-link[data-doctype='${type}']`;
            if (frm.doc.status === 'Rejected') {
                $(selector).hide();
                $(".inner-group-button").hide();
            } else {
                $(selector).show();
            }
        });
        frappe.call({
            method: "frappe.client.get_list",
            args: {
              doctype: "Interview",
              filters: {
                job_applicant: frm.doc.name,
              },
            },
            callback: function (response) {
              if (!response.exc) {
                if (response.message.length == 0) {
                  $(".document-link[data-doctype='Interview']").hide();
                } else {
                  $(".document-link[data-doctype='Interview']").show();
                }
              }
            },
          });
    },
    before_save(frm) {
		// frm.set_value("status", "Interview Pending");
    
    let contact = {
      "doctype": "Contact",
      "first_name": frm.doc.applicant_name,
      "email_id": frm.doc.email_id
    }
    if (frm.doc.phone_number) {
      contact.phone_number = frm.doc.phone_number; // Replace with the actual phone number
    }

    frappe.db.insert(contact)
	}
    
});