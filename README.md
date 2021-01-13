# EasyUpgrade

Disruptive patching requires coordination between several teams within an enterprise organization.

This application eases these efforts by: grouping servers by customer, identifying unsupported software components, and vulnerability items.

Additionally, by using the pysnow module, ServiceNow change requests can be generated based on this data, with appropriate tasks assigned to corresponding teams.

Data about servers is read from a csv, processed by the python code, and dynamically generates: a jinja-based html page with details about the server group / a corresponding ServiceNow change request.
