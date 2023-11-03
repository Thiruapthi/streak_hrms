
frappe.ui.form.on("Job Applicant", {
  refresh: function (frm) {
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

    if (frm.doc.status === "Rejected") {
      var transactionsContainer = document.querySelector('.transactions');
      var formDocumentsContainer = transactionsContainer.querySelector('.form-documents');
      var rowElement = formDocumentsContainer.querySelector('.row');

      rowElement.classList.add('d-flex', 'flex-column');
    }
    else {
      var transactionsContainer = document.querySelector('.transactions');
      var formDocumentsContainer = transactionsContainer.querySelector('.form-documents');
      var rowElement = formDocumentsContainer.querySelector('.row');

      rowElement.classList.remove('d-flex', 'flex-column');
    }
  },
  after_save(frm) {
    // frm.set_value("status", "Interview Pending");
    frappe.call({
      method: 'hyde_app.api.Interview_Rounds',  // Replace with your method and module name
      args: {
        'job_titles': frm.doc.job_title,
        'doc': frm.doc  // Pass any relevant arguments
      },
      callback: function (r) {
        if (!frm.doc.custom_rounds || frm.doc.custom_rounds.length === 0) {
          for (let i = 0; i < r.message.length; i++) {
            let row = frm.add_child('custom_rounds', {
              interview_rounds: r.message[i].interview_rounds,
              qty: 2
            });
          }
        frm.refresh_field('items');
        cur_frm.refresh_fields('rounds')
        frm.save()
        }
        
      }
    });

  },

  validate(frm) {
		// frm.set_value("status", "Interview Pending");
    if (!frm.doc.contact_created) {
    frappe.call({
      method: 'hyde_app.api.job_applicant_contact',  // Replace with your method and module name
      args: {
          'email': frm.doc.email_id,  // Pass any relevant arguments
          'mobile' : frm.doc.phone_number,
          'name' : frm.doc.applicant_name
        },
      callback:function(r){
        cur_frm.refresh_fields('rounds')
        frm.doc.contact_created = 1
        frm.save()
      }
      });
    }
    
	}
})

frappe.realtime.on("applicant_status_update", function (data) {
  cur_frm.reload_doc()

})