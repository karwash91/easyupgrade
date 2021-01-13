# easyupgrade

Disruptive patching requires coordination of numerous teams.

This application eases these efforts by: grouping servers by customer, identifying unsupported software components, and vulnerability items.

Additionally, ServiceNow change requests can be generated based on these details, with corresponding tasks assigned to necessary teams.

Data about servers is read from a csv, processed by the python code, and generates: an html page with details about the server group / a corresponding ServiceNow change request.
