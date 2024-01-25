frappe.ui.form.on("Opportunity", {
    sales_stage: function (frm) {
        frappe.db.get_value('Sales Stage', frm.doc.sales_stage, 'custom_probability').then((res) => {
        cur_frm.set_value('probability', res.message.custom_probability)
        frm.set_value("custom_test",frm.doc.sales_stage);
        })
      }
})

frappe.ui.form.on("Opportunity", {
  refresh: function (frm) {
      frm.set_value("sales_stage",frm.doc.custom_test);
      }
})