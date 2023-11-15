frappe.ui.form.ControlAttach.prototype.on_upload_complete = async function (
    attachment
  ) {
    if (this.frm) {
      await this.parse_validate_and_set_in_model(attachment.file_url);
      this.frm.attachments.update_attachment(attachment);
      if (this.frm.doc.doctype !== "Appointment Letter") {
        this.frm.doc.docstatus == 1 ? this.frm.save("Update") : this.frm.save();
      }
    }
    this.set_value(attachment.file_url);
  };