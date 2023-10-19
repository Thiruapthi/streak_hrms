frappe.ui.form.on('Role', {
     refresh: function(frm) {  
            fetchAndDisplayRolePermissions(frm);
        }     
});


function fetchAndDisplayRolePermissions(frm) {
    frappe.call({
        method: 'hyde_app.role_perms_api.get_role_permissions',
        args: {
            "role": frm.doc.name
        },
        callback: function(response) {
            if (response.message.length>=1) {
                const formPageElement = document.querySelector('.form-page');
                const newClass = 'my-custom-class';
                formPageElement.classList.add(newClass);
                
                const customStyle = `
                .my-custom-class {
                min-width: min-content;
                }
                `;

                const styleElement = document.createElement('style');
                styleElement.innerHTML = customStyle;               
                document.head.appendChild(styleElement);

                const container = frm.page.main.find('.form-page');
                container.find('table').remove();
                const permissions = response.message;

                // Create a Bootstrap table
                const table = $('<table>').addClass('table table-striped my-custom-table');

                const customStyleTable = `
                .my-custom-table {
                margin: 0px;
                }
                `;
        
                const styleElementTable = document.createElement('style');
                styleElementTable.innerHTML = customStyleTable;               
                document.head.appendChild(styleElementTable);
                
                container.append(table)

                // Create table header
                table.append(`
                    <thead>
                    <tr>
                        <th colspan="16">Role Permissions</th>
                    </tr>
                        <tr>
                            <th>Doctype Name</th>                            
                            <th>Select</th>
                            <th>Read</th>
                            <th>Write</th>
                            <th>Create</th>
                            <th>Delete</th>
                            <th>Submit</th>
                            <th>Cancel</th>
                            <th>Amend</th>
                            <th>Print</th>
                            <th>Email</th>
                            <th>Report</th>
                            <th>Import</th>
                            <th>Export</th>
                            <th>Set User Permissions</th>
                            <th>Share</th>
                        </tr>
                    </thead>
                `);

                // Create table body
                const tbody = $('<tbody>');
                table.append(tbody);

                // Iterate through permissions and create rows
                for (const permission of permissions) {
                    tbody.append(`
                        <tr>
                            <td>${permission.parent}</td>
                            <td>${permission.select ? '✔' : ''}</td>
                            <td>${permission.read ? '✔' : ''}</td>
                            <td>${permission.write ? '✔' : ''}</td>
                            <td>${permission.create ? '✔' : ''}</td>
                            <td>${permission.delete ? '✔' : ''}</td>
                            <td>${permission.submit ? '✔' : ''}</td>
                            <td>${permission.cancel ? '✔' : ''}</td>
                            <td>${permission.amend ? '✔' : ''}</td>
                            <td>${permission.print ? '✔' : ''}</td>
                            <td>${permission.email ? '✔' : ''}</td>
                            <td>${permission.report ? '✔' : ''}</td>
                            <td>${permission.import ? '✔' : ''}</td>
                            <td>${permission.export ? '✔' : ''}</td>
                            <td>${permission.set_user_permissions ? '✔' : ''}</td>
                            <td>${permission.share ? '✔' : ''}</td>

                        </tr>
                    `);
                    
                        tbody.addClass('table-info');
                    
                }
            }
        }
    });
}
