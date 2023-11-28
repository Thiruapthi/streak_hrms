frappe.ui.form.on('Interview Feedback',{   
validate(frm) {
        for (let i = 0; i < cur_frm.doc.skill_assessment.length; i++) {
            const originalRating = cur_frm.doc.skill_assessment[i].rating;
            const roundedRating = roundToEven(originalRating);
            cur_frm.doc.skill_assessment[i].rating = roundedRating;
            if (cur_frm.doc.skill_assessment[i].rating === 0.2) {
              cur_frm.doc.skill_assessment[i].custom_grading = 'Not Acceptable';
            } else if (cur_frm.doc.skill_assessment[i].rating === 0.4) {
              cur_frm.doc.skill_assessment[i].custom_grading = 'Poor';
            } else if (cur_frm.doc.skill_assessment[i].rating === 0.6) {
              cur_frm.doc.skill_assessment[i].custom_grading = 'Average';
            } else if (cur_frm.doc.skill_assessment[i].rating === 0.8) {
              cur_frm.doc.skill_assessment[i].custom_grading = 'Good';
            } else if (cur_frm.doc.skill_assessment[i].rating === 1) {
              cur_frm.doc.skill_assessment[i].custom_grading = 'Exceptional';
            }
        }
    },

    after_save(frm) {
      frappe.call({
          method: 'hyde_app.api.get_interviewers_list',
          args: {
            'interview': frm.doc.interview,
            'result':frm.doc.result
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
