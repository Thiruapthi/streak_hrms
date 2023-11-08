frappe.ui.form.on('Interview Feedback',{   
validate(frm) {
        console.log('78964');
        for (let i = 0; i < cur_frm.doc.skill_assessment.length; i++) {
            const originalRating = cur_frm.doc.skill_assessment[i].rating;
            const roundedRating = roundToEven(originalRating);
            cur_frm.doc.skill_assessment[i].rating = roundedRating;
        }
    },

    after_save(frm) {
      var interview = frm.doc.interview
      frappe.call({
          method: 'hyde_app.api.get_interviewers_list',
          args: {
            'interview': interview
          }
        });
  }
    
})

function roundToEven(value) {
    value = value*10;
    let roundedValue = Math.round(value);
    if (roundedValue % 2 !== 0) {
        roundedValue += 1;
    }
    return roundedValue/10;
}
