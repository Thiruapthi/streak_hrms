frappe.standard_pages["Workspaces"] = function () {
    var wrapper = frappe.container.add_page("Workspaces");

    frappe.ui.make_app_page({
        parent: wrapper,
        name: "Workspaces",
        title: __("Workspace"),
    });

    frappe.workspace = new frappe.views.Workspace(wrapper);
    $(wrapper).bind("show", function () {
        frappe.workspace.show();
    });

    $(document).ready(function () {
        frappe.call({
            method: "streak_hrms.get_roles.get_all_roles",
            callback: function (r) {
                if (r.message.includes("Employee") && r.message.length <= 3) {
                    $(".input-group.search-bar.text-muted").hide()
                    setTimeout(function () {
                        $(".sidebar-item-container[item-name='Recruitment']").hide();
                    }, 1000)
                }
            }
        })
    });

};