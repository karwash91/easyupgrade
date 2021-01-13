#!/usr/bin/python3

# Title: kw_easyupgrade_app.py
# Author: Kareem Washington
# Date Last Modified: 01/11/2020
# Disruptive patching requires coordination between several teams within an enterprise organization.
# This application eases these efforts by: grouping servers by customer, identifying unsupported software components, and vulnerability items.
# Additionally, by using the pysnow module, ServiceNow change requests can be generated based on this data, with appropriate tasks assigned to corresponding teams.
# Data about servers is read from a csv, processed by the python code, and dynamically generates: a jinja-based html page with details about the server group / a corresponding ServiceNow change request.

# import modules
import warnings
warnings.simplefilter("ignore", UserWarning)
import cgi, csv, yaml, pysnow, jinja2
from datetime import datetime, timezone

# import config file
kw_easyupgrade_conf_file = open('/opt/freeware/apache/share/cgi-bin/kw_upgrade_inventory/confs/kw_easyupgrade_conf.yml', 'r')
conf = yaml.load(kw_easyupgrade_conf_file, Loader = yaml.FullLoader)

# import html template
jinja2_loader = jinja2.FileSystemLoader('/opt/freeware/apache/share/cgi-bin/kw_upgrade_inventory/confs/kw_easyupgrade_form.txt')
jinja2_env = jinja2.Environment(loader = jinja2_loader)
form_template = jinja2_env.get_template('')

# set environment lists
env_tdc_list = conf['env']['tdc'] # list of all tdc environments by name (TRAINING, SANDBOX, etc.)
env_prod_list = conf['env']['prod'] # list of all prod environments by name
env_dr_list = conf['env']['dr'] # list of all dr environments by name
env_prod_dr_list = env_prod_list + env_dr_list
env_all_list = env_tdc_list + env_prod_dr_list

# set easyupgrade_csv where server data lives
easyupgrade_csv = conf['dirs']['csvs'] + conf['files']['easyupgrade_csv']

# csv reader function
def csv_reader(csv_file):
    open_csv = open(csv_file, 'r')
    csv_reader = csv.reader(open_csv)
    return csv_reader

# find the customer name based on the server name selected
def get_cust_name(form_serv_name, csv_file):
    cust_name = ""
    while cust_name == "": # read customer names until server name matches
        for row in csv_reader(csv_file):
            if form_serv_name == row[0]:
                cust_name = row[1]
    return cust_name

# find the lowest environment (TDC, PROD, PROD / DR, DR) where servers are not at the latest OS
def get_next_env_to_upgrade(inventory_dict, form_next_env_to_upgrade):
    if form_next_env_to_upgrade == "Default":
        # initialize variables for next environment to upgrade
        next_env_to_upgrade = "None"
        tdc = "No"
        prod = "No"
        dr = "No"
        # initialize list for environments with servers not at the latest OS
        envs_list = []
        # iterate through dictionary to find relevant environments
        for serv, value in inventory_dict.items():
            if value['serv_curr_os'] != conf['vers']['latest_os']:
                envs_list.append(value['serv_env'])
        # determine what environments were found
        if any(env in env_tdc_list for env in envs_list):
            tdc = "Yes"
        if any(env in env_prod_list for env in envs_list):
            prod = "Yes"
        if any(env in env_dr_list for env in envs_list):
            dr = "Yes"
        # set the next environment to upgrade based on custom rules
        while next_env_to_upgrade == "None":
            if tdc == "Yes":
                next_env_to_upgrade = "TDC"
                break
            if prod == "Yes" and dr == "Yes":
                next_env_to_upgrade = "PROD / DR"
                break
            if prod == "Yes":
                next_env_to_upgrade = "PROD"
                break
            if dr == "Yes":
                next_env_to_upgrade = "DR"
                break
    else:
        next_env_to_upgrade = form_next_env_to_upgrade
    return next_env_to_upgrade

# create a dictionary based on the next environment to upgrade (TDC, PROD, etc.)
def get_to_be_upgraded(next_env_to_upgrade, inventory_dict):
    if next_env_to_upgrade == "TDC":
        env_list = env_tdc_list
    if next_env_to_upgrade == "PROD / DR":
        env_list = env_prod_dr_list
    if next_env_to_upgrade == "PROD":
        env_list = env_prod_list
    if next_env_to_upgrade == "DR":
        env_list = env_dr_list
    to_be_upgraded_dict = {}  # dictionary narrowed down to only servers where upgraded is needed
    for serv, value in inventory_dict.items():
        if (value['serv_curr_os'] != conf['vers']['latest_os']) and (value['serv_env'] in env_list):
            to_be_upgraded_dict[serv] = {
                'serv_name': value['serv_name'],
                'serv_curr_os': value['serv_curr_os'],
                'serv_env': value['serv_env'],
                'lob_email': value['lob_email'],
                'is_powerha': value['is_powerha'],
                'is_vormetric': value['is_vormetric'],
                'is_oracle': value['is_oracle'],
                'is_db2': value['is_db2'],
                'is_sap': value['is_sap'],
                'is_sap_prod': value['is_sap_prod'],
                'is_gpfs': value['is_gpfs'],
                'is_centrify': value['is_centrify'],
                'is_java5': value['is_java5'],
                'is_java6': value['is_java6'],
                'is_java7': value['is_java7'],
                'is_java8': value['is_java8'],
                'is_retired': value['is_retired'],
                'snow_sys_id': value['snow_sys_id'],
                'is_enclave': value['is_enclave'],
                'is_guardium': value['is_guardium']
                }
    return to_be_upgraded_dict

# create change request function
def create_chg_request(conn, chg_network_id, chg_start_time, chg_end_time, cmdb_ci, chg_short_description, chg_description, u_role, u_test_results):
    table = conn.resource(api_path = conf['snow']['change_request_api'])
    payload = {
        'assigned_to': chg_network_id,
        'start_date': chg_start_time + ":00",
        'end_date': chg_end_time + ":00",
        'cmdb_ci': cmdb_ci,
        'short_description': chg_short_description,
        'description': chg_description,
        'u_role': u_role,
        'u_test_results': u_test_results,
        'type': conf['snow']['type'],
        'test_plan': conf['snow']['standard_plan'],
        'change_plan': conf['snow']['standard_plan'],
        'u_verification_plan': conf['snow']['standard_plan'],
        'backout_plan': conf['snow']['standard_plan'],
        'u_related_release': conf['snow']['u_related_release'],
        'category': conf['snow']['category'],
        'u_subcategory': conf['snow']['u_subcategory'],
        'u_estimated_downtime': conf['snow']['u_estimated_downtime'],
        'u_backout_duration': conf['snow']['u_backout_duration'],
        'assignment_group': conf['snow']['assignment_group']
        }
    res = table.create(payload = payload)
    return res.all()

# update change request function
def update_chg_request(conn, chg_number):
    table = conn.resource(api_path = conf['snow']['change_request_api'])
    payload = {
        'type': "Routine"
        }
    table.update(query={'number': chg_number}, payload = payload)

# get list of server names to be upgraded function
def servs_to_upgrade(to_be_upgraded_dict):
    servs_to_upgrade_list = []
    for serv, value in to_be_upgraded_dict.items():
            servs_to_upgrade_list.append(serv)
    return servs_to_upgrade_list

# get list of server ServiceNow sys_id's for setting affected CI's function
def sys_ids_to_upgrade(to_be_upgraded_dict):
    sys_ids_to_upgrade_list = []
    for serv, value in to_be_upgraded_dict.items():
            sys_ids_to_upgrade_list.append(value['snow_sys_id'])
    return sys_ids_to_upgrade_list

# set affected CI's for a change request function
def set_affected_cis(conn, chg_sys_id, sys_ids_to_upgrade):
    table = conn.resource(api_path = conf['snow']['affected_api'])
    for sys_id in sys_ids_to_upgrade:
        if sys_id != "null": # skip CI's where sys_id is null
            payload = {
                'ci_item': sys_id,
                'task': chg_sys_id
                }
            table.create(payload = payload)

# create ctask function
def create_ctask(conn, chg_sys_id, chg_start_time, chg_end_time, cmdb_ci, form_create_chg, to_be_upgraded_dict):
    ctask_dict = [] # set empty list for ctask dictionary
    table = conn.resource(api_path = conf['snow']['task_api'])
    for val in conf['dynamic_ctasks']: # for every ctask in the config file's list of ctasks
        relevant_servs = [] # this will be the list of relevant servers when condition is triggered
        for serv, value in to_be_upgraded_dict.items():
            vers = value[val] # version of software component for this server
            trigger = conf['dynamic_ctasks'][val]['yes_action'] # list of conditions where action shoud be triggered
            if any(string in vers for string in trigger):
                if str(val) != "is_guardium":  # guardium ctasks only become relevant if upgrading from a specfic OS version
                    relevant_servs.append(value['serv_name'])
                else:
                    if "7100" in value['serv_curr_os']: # guardium ctasks only become relevant if upgrading from a specfic OS version
                        relevant_servs.append(value['serv_name'])
        if len(relevant_servs) != 0:
            short_description = conf['dynamic_ctasks'][val]['ctask']['short_description']
            group = conf['dynamic_ctasks'][val]['ctask']['group']
            ctask = dict(short_description = short_description, description = relevant_servs, group = group)
            ctask_dict.append(ctask) # add ctask elements to dictionary
    for val in conf['static_ctasks']: # for every ctask in the config file's list of ctasks
        relevant_servs = [] # this will be the list of relevant servers when condition is triggered
        for serv, value in to_be_upgraded_dict.items():
            relevant_servs.append(value['serv_name'])
        short_description = conf['static_ctasks'][val]['ctask']['short_description']
        group = conf['static_ctasks'][val]['ctask']['group']
        ctask = dict(short_description = short_description, description = relevant_servs, group = group)
        ctask_dict.append(ctask) # add ctask elements to dictionary
    if form_create_chg == "Yes":
        for ctask in ctask_dict: # for every ctask discovered to be needed, create the ctask in ServiceNow
            description = ctask['description']
            if ctask['short_description'] == "Stop and Start Applications": # conditional logic to add in a DO NOT CLOSE header for this particular ctask
                description = "***DO NOT CLOSE***\n\nPending LOB response with correct server names.\n\n" + "\n".join(description)
            else:
                description = "\n".join(description) # otherwise, the relevant servers will server as the description
            payload = {
                'change_request': chg_sys_id,
                'short_description': ctask['short_description'],
                'description': description,
                'assignment_group': ctask['group'],
                'state': "1",
                'expected_start': chg_start_time + ":00",
                'due_date': chg_end_time + ":00",
                'cmdb_ci': cmdb_ci
            }
            table.create(payload = payload)
    return ctask_dict

# convert the csv file into dictionary for use function
def convert_csv_to_dict(cust_name, csv_file):
    inventory_dict = {} # initialize empty dictionary
    for row in csv_reader(csv_file):
        if row[1] == cust_name: # append dictionary if customer name matches
            inventory_dict[row[0]] = {
                'serv_name': row[0],
                'cust_name': row[1],
                'serv_curr_os': row[2],
                'serv_env': row[3],
                'lob_email': row[4],
                'is_powerha': row[5],
                'is_vormetric': row[6],
                'is_oracle': row[7],
                'is_db2': row[8],
                'is_sap': row[9],
                'is_sap_prod': row[10],
                'is_gpfs': row[11],
                'is_centrify': row[12],
                'is_java5': row[13],
                'is_java6': row[14],
                'is_java7': row[15],
                'is_java8': row[16],
                'serv_uptime': row[17],
                'serv_frame': row[18],
                'is_HPSA': row[19],
                'is_SN': row[20],
                'is_PV': row[21],
                'is_retired': row[22],
                'snow_sys_id': row[23],
                'frame_lpars': row[24],
                'frame_cpu_total': row[25],
                'frame_cpu_enabled': row[26],
                'frame_mem_total': row[27],
                'frame_mem_enabled': row[28],
                'frame_maint_end': row[29],
                'frame_maint_cost': row[30],
                'is_enclave': row[31],
                'is_guardium': row[32]
                }
    return inventory_dict

# function to set html upgrade table
def set_upgrade_table_html(inventory_dict, latest_os):
    html = []  # set empty list
    for env in env_all_list:  # by looping through each environment in order, this makes sure TDC servers appear first, PROD second, DR last
        for serv, value in inventory_dict.items():
            if value['serv_env'] in env:
                # set basic fields
                serv_name = value['serv_name']
                serv_curr_os = value['serv_curr_os']
                serv_env = value['serv_env']
                # set some custom fields based on if the server is already upgraded, if it is in the enclave environment, etc.
                if latest_os not in serv_curr_os:
                    latest_os_span_style = conf['html']['span_style_default']
                    if value['is_enclave'] == "yes_enclave":
                        serv_env_span_style = conf['html']['span_style_purple']
                        serv_env = "ENCLAVE " + serv_env
                    else:
                        serv_env_span_style = conf['html']['span_style_default']
                else:
                    serv_env_span_style = conf['html']['span_style_green']
                    latest_os_span_style = conf['html']['span_style_green']
                    serv_env = "Already Upgraded"
                    latest_os = "Already Upgraded"
                # set each row of the html table with the variables above
                row = dict(serv_name = serv_name, serv_curr_os = serv_curr_os, serv_env_span_style = serv_env_span_style,
                           serv_env = serv_env, latest_os_span_style = latest_os_span_style, latest_os = latest_os)
                html.append(row)
    return html

# function to set html ctask table
def set_ctask_table_html(ctask_dict):
    html = []  # set empty list
    for ctask in ctask_dict:
        # set each row of the html table
        row = dict(task = ctask['short_description'], relevant_servs = ", ".join(ctask['description']), assignment_group = ctask['group'])
        html.append(row)
    return html

# front-end form input attributes
class EasyUpgradeForm:
    def __init__(self):
        submission = cgi.FieldStorage()
        self.serv_name = submission.getvalue('serv_name') # Select a server name
        self.create_chg = submission.getvalue('create_chg') # Create a CHG?
        self.next_env_to_upgrade = submission.getvalue('next_env_to_upgrade') # Upgrade which environment?
        self.chg_network_id = submission.getvalue('chg_network_id') # Select your network ID:
        self.chg_date = submission.getvalue('chg_date') # Select the CHG date:
        self.chg_start_time = submission.getvalue('chg_start_time') # Select the CHG start time:
        self.chg_end_time = submission.getvalue('chg_end_time') # Select the CHG end time:
        self.testing = submission.getvalue('testing') # Just testing?

# ServiceNow connection attributes
class SnowConn:
    def __init__(self, testing, test_instance, prod_instance, user, password):
        if testing == "Yes": # Just testing?
            self.instance = test_instance
        else:
            self.instance = prod_instance
        self.conf = pysnow.Client(instance = self.instance, user = user, password = password)

# dates and times attributes of the change request
class DatesTimes:
    # convert to ServiceNow timezone
    def convert_tz(self, datetime_obj):
        return datetime_obj.replace(tzinfo = None).astimezone(tz = timezone.utc)
    def __init__(self, chg_date, chg_start_time, chg_end_time):
        # from EasyUpgradeForm
        self.start_time = chg_date + " " + chg_start_time
        self.end_time = chg_date + " " + chg_end_time
        # convert to datetime objects
        self.chg_date_obj = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M')
        self.start_time_obj = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M')
        self.end_time_obj = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M')
        # convert to human-readable strings
        self.chg_date_str = self.chg_date_obj.strftime('%a, %b %d')
        self.start_time_str = self.start_time_obj.strftime('%H:%M')
        self.end_time_str = self.end_time_obj.strftime('%H:%M')
        # convert to ServiceNow timezone
        self.start_time_obj_converted_tz = self.convert_tz(self.start_time_obj)
        self.end_time_obj_converted_tz = self.convert_tz(self.end_time_obj)
        self.chg_start_time = self.start_time_obj_converted_tz.strftime('%Y-%m-%d %H:%M')
        self.chg_end_time = self.end_time_obj_converted_tz.strftime('%Y-%m-%d %H:%M')

# define inventory dictionary. this contains data about inventory belonging to a specific customer
class Inventory:
    def __init__(self, cust_name, csv_file, form_serv_name):
        self.cust_name = cust_name
        self.dict = convert_csv_to_dict(cust_name, csv_file)
        self.email_to = self.dict[form_serv_name]['lob_email']

# define attributes of specifically servers to be upgraded
class ToBeUpgraded:
    def __init__(self, next_env_to_upgrade, inventory_dict):
        self.next_env_to_upgrade = next_env_to_upgrade
        self.dict = get_to_be_upgraded(next_env_to_upgrade, inventory_dict)

# define change request attributes
class CHGRequest:
    def __init__(self, cust_name, next_env_to_upgrade, to_be_upgraded_dict, form_create_chg, conn, chg_network_id, chg_start_time, chg_end_time):
        self.cust_name = cust_name
        self.next_env_to_upgrade = next_env_to_upgrade
        self.servs_to_upgrade = servs_to_upgrade(to_be_upgraded_dict)
        self.servs_count = len(self.servs_to_upgrade)
        # only if "Yes" selected in form and there are servers to be upgraded will change be created
        if form_create_chg == "Yes" and self.servs_count != 0:
            self.cmdb_ci = self.servs_to_upgrade[0]
            # set the u_role based on the next environment to be upgraded
            if next_env_to_upgrade == "TDC":
                self.u_role = "Test"
            if (next_env_to_upgrade == "PROD / DR") or (next_env_to_upgrade == "PROD"):
                self.u_role = "Production"
            if next_env_to_upgrade == "DR":
                self.u_role = "Disaster Recovery"
            self.short_description = conf['snow']['short_description'] % (self.servs_count, self.next_env_to_upgrade, self.cust_name, conf['vers']['latest_os'])
            self.description = self.short_description + "\n\n" + "\n".join(self.servs_to_upgrade)
            self.sys_ids_to_upgrade = sys_ids_to_upgrade(to_be_upgraded_dict)
            self.u_test_results = conf['snow']['u_test_results'] % (conf['vers']['latest_os'])
            # get back results of change request creation
            res = create_chg_request(conn, chg_network_id, chg_start_time, chg_end_time, self.cmdb_ci, self.short_description, self.description, self.u_role, self.u_test_results)
            self.sys_id = res[0]['sys_id']
            self.number = res[0]['number']
            self.link = res[0]['u_task_url_link']
            set_affected_cis(conn, self.sys_id, self.sys_ids_to_upgrade)
            if next_env_to_upgrade == "TDC":
                update_chg_request(conn, self.number)
        else:
            self.sys_id = ""
            self.number = ""
            self.link = ""
            self.cmdb_ci = ""
        self.ctask_disk = create_ctask(conn, self.sys_id, chg_start_time, chg_end_time, self.cmdb_ci, form_create_chg, to_be_upgraded_dict)

# define html upgrade table attributes
class HTMLContent:
    def __init__(self, inventory_dict, ctask_dict, latest_os):
        self.upgrade_table = set_upgrade_table_html(inventory_dict, latest_os)
        self.ctask_table = set_ctask_table_html(ctask_dict)

# define alert attributes. these are used to establish conditional logic for creating the resulting html page
class Alert:
    def __init__(self, cust_name, servs_count, form_testing,form_create_chg):
        # if server is being retired, set alert
        if "Retiring" in cust_name:
            self.retired_alert = "Yes"
        else:
            self.retired_alert = "No"
        # if no servers are in the count of servers to be upgraded, there were no matches. set alert
        if servs_count == 0:
            self.no_match_alert = "Yes"
        else:
            self.no_match_alert = "No"
        # if creating a change request, set alert
        if form_create_chg == "Yes":
            self.create_chg_alert = "Yes"
            # if just testing this application, set alert
            if form_testing == "Yes":
                self.testing_chg_alert = "Yes"
            else:
                self.testing_chg_alert = "No"
        else:
            self.create_chg_alert = "No"
            self.testing_chg_alert = "No"

# main function
def main():
    form = EasyUpgradeForm()
    cust_name = get_cust_name(form.serv_name, easyupgrade_csv)
    inventory = Inventory(cust_name, easyupgrade_csv, form.serv_name)
    next_env_to_upgrade = get_next_env_to_upgrade(inventory.dict, form.next_env_to_upgrade)
    to_be_upgraded = ToBeUpgraded(next_env_to_upgrade, inventory.dict)
    snow_conn = SnowConn(form.testing, conf['snow']['test']['instance'], conf['snow']['prod']['instance'], conf['snow']['user'], conf['snow']['password'])
    dates_times = DatesTimes(form.chg_date, form.chg_start_time, form.chg_end_time)
    change_request = CHGRequest(cust_name, next_env_to_upgrade, to_be_upgraded.dict, form.create_chg, snow_conn.conf, form.chg_network_id, dates_times.chg_start_time, dates_times.chg_end_time)
    html_content = HTMLContent(inventory.dict, change_request.ctask_disk, conf['vers']['latest_os'])
    alert = Alert(cust_name, change_request.servs_count, form.testing, form.create_chg)
    kw_easyupgrade_form_html = form_template.render(cust_name = str(cust_name),
                                                    next_env_to_upgrade = str(next_env_to_upgrade),
                                                    retired_alert = str(alert.retired_alert),
                                                    create_chg_alert = str(alert.create_chg_alert),
                                                    no_match_alert = str(alert.no_match_alert),
                                                    testing_chg_alert = str(alert.testing_chg_alert),
                                                    chg_request_link = str(change_request.link),
                                                    chg_request_number = str(change_request.number),
                                                    chg_date_str = str(dates_times.chg_date_str),
                                                    start_time_str = str(dates_times.start_time_str),
                                                    end_time_str = str(dates_times.end_time_str),
                                                    email_from = str(conf['html']['email_from']),
                                                    email_to = str(inventory.email_to),
                                                    email_subject = str(conf['html']['email_subject'] % (cust_name)),
                                                    email_greeting = str(conf['html']['email_greeting'] % (next_env_to_upgrade)),
                                                    email_ctask_heading = str(conf['html']['email_ctask_heading']),
                                                    email_sig = str(conf['html']['email_sig']),
                                                    upgrade_table_html = html_content.upgrade_table,
                                                    ctask_table_html = html_content.ctask_table,
                                                    start_over_link = str(conf['html']['start_over_link'])
                                                    )
    print(conf['html']['content_type'] + kw_easyupgrade_form_html)

if __name__ == "__main__":
    main()
