
frappe.ui.form.on("Job Applicant", {
    refresh: function(frm) {
        var interviewButton = $(".document-link[data-doctype='Interview'] button[data-doctype='Interview']");
        interviewButton.remove();
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
                console.log(response.message.length);
                if (response.message.length == 0) {
                  console.log(response.message.length);
                  $(".document-link[data-doctype='Interview']").hide();
                } else {
                  $(".document-link[data-doctype='Interview']").show();
                }
              }
            },
          });
    },
    before_save(frm) {
        console.log("hello")
		frm.set_value("status", "Interview Pending");
	}
    
});