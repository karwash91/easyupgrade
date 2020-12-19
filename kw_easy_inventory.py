#!/usr/bin/python3

# Title: kw_easy_upgrade.py
# Author: Kareem Washington
# Date Last Modified: 11/30/2020
# The function of this application is to create and manage change requests for upgrading server OS across customer groups.

# import modules
import warnings
warnings.simplefilter("ignore", UserWarning)
import cgi, csv, pysnow
from datetime import datetime, timedelta

# get form data
class form_data():
    form_data_submission = cgi.FieldStorage()
    serv_name = form_data_submission.getvalue('serv_name')
    create_chg = form_data_submission.getvalue('create_chg')
    chg_network_id = form_data_submission.getvalue('chg_network_id')
    chg_date = form_data_submission.getvalue('chg_date')
    chg_start_time = form_data_submission.getvalue('chg_start_time')
    chg_end_time = form_data_submission.getvalue('chg_end_time')
    testing = form_data_submission.getvalue('testing')
form = form_data()

# set user-defined vars
class user_def_vars():
    # static vars
    latest_serv_os = "7.5"
    tdc_env = ["TRAINING", "SANDBOX", "TEST", "DEVELOPMENT"]
    prod_env = ["PRODUCTION"]
    dr_env = ["DISASTER RECOVERY"]
    kw_scripts_dir = "/pathtoscriptsdir/"
    kw_csvs_dir = "/pathtocsvsdir/"
    kw_confs_dir = "/pathtoconfsdir/"
    merged_csv_file = kw_csvs_dir + "merged_csv_file"
    # convert dates
    form_start_time = form.chg_date + " " + form.chg_start_time
    form_end_time = form.chg_date + " " + form.chg_end_time
    hum_chg_date_obj = datetime.strptime(form_start_time, '%Y-%m-%d %H:%M')
    hum_start_time_obj = datetime.strptime(form_start_time, '%Y-%m-%d %H:%M')
    hum_end_time_obj = datetime.strptime(form_end_time, '%Y-%m-%d %H:%M')
    hum_chg_date = hum_chg_date_obj.strftime('%a, %b %d')
    hum_start_time = hum_start_time_obj.strftime('%H:%M')
    hum_end_time = hum_end_time_obj.strftime('%H:%M')
    form_start_time_obj = datetime.strptime(form_start_time, '%Y-%m-%d %H:%M') + timedelta(hours=4)
    form_end_time_obj = datetime.strptime(form_end_time, '%Y-%m-%d %H:%M') + timedelta(hours=4)
    # snow vars
    chg_start_time = form_start_time_obj.strftime('%Y-%m-%d %H:%M:00')
    chg_end_time = form_end_time_obj.strftime('%Y-%m-%d %H:%M:00')
    snow_test_conf = kw_confs_dir + "snow_test.conf"
    snow_prod_conf = kw_confs_dir + "snow_prod.conf"
    chg_category = "Software"
    chg_subcategory = "Technology"
    chg_assignment_group = "My-IT-Group"
    chg_type = "Comprehensive"
    u_related_release = "My-Related-Release"
    standard_plan = "https://linktostandardplan"
    u_test_results = "Server(s) was upgraded successfully to " + latest_serv_os + "."
    u_estimated_downtime = "1970-01-01 09:00:00"
    u_backout_duration = "1970-01-01 05:30:00"
    # find cust_name
    open_merged_csv_file = open(merged_csv_file, 'r')
    merged_csv_file_reader = csv.reader(open_merged_csv_file)
    cust_name = ""
    serv_name = form.serv_name
    while cust_name == "":
        for row in merged_csv_file_reader:
            if serv_name == row[0]:
                cust_name = row[1]
    # set email vars
    email_from = "My-IT-Group@domain.com"
    email_sub = "OS Upgrades Needed for: " + cust_name[4:] + " Servers"
    email_greeting = "<p>Hello,<br><br>We need to carry out disruptive OS upgrades on the servers listed below.<br><br>Can you provide a four-hour outage windows for each environment?</p>"
    email_sig = "<p>Automated e-mail sent via <strong>Python3 | My-IT-Group</strong></p>"
    td_tag = "<td>"
    tr_tag = "<tr>"
    th_tag = "<th>"
    tab_tag = "<table id=\"myTable\"><tr>"
    span_default = "<span class=\"span_style_default\">"
    span_green = "<span class=\"span_style_green\">"
    span_purple = "<span class=\"span_style_purple\">"
    span_orange = "<span class=\"span_style_orange\">"
    span_red = "<span class=\"span_style_red\">"
    span_gray = "<span class=\"span_style_gray\">"
    div_box = "<div class=\"div_box\"><br><span>"
    span_big_num = "</span><br><span class=\"span_big_num\">"
    span_caption = "</span><br><span class=\"span_caption\">"
    close_span_div = "</span></div>"
    close_span = "</span>"
    close_tab = "</table><br>"
    close_td_tag = "</td>"
    close_tr_tag = "</tr>"
    close_th_tag = "</th>"
    tab_upgrade_header = tr_tag + th_tag + "Name" + close_th_tag + th_tag + "Current OS" + close_th_tag + th_tag + "Environment" + close_th_tag + th_tag + "Upgrade OS to" + close_th_tag + th_tag + "Date / Time" + close_th_tag + close_tr_tag
    tab_ctask_header = tr_tag + th_tag + "TASK" + close_th_tag + th_tag + "Relevant Servers" + close_th_tag + th_tag + "Assignment Group" + close_th_tag + th_tag + "Assigned to" + close_th_tag + close_tr_tag
    # set ctask vars
    ctask_greeting = "<p>Also, please confirm the CTASKs listed below:</p>"
    ctask_dict = {
        "iossavdb" : {
            "short_description": "Information Only: Stop, Start, and Validate Databases",
            "group" : "IT-Oracle-Group"
        },
        "ssavdb" : {
            "short_description": "Stop, Start, and Validate Databases",
            "group" : "IT-DB2-Group"
        },
        "sasa": {
            "short_description": "Stop and Start Applications",
            "group": "My-IT-Group"
        },
        "va": {
            "short_description": "Validate Applications",
            "group": "My-IT-Group"
        },
        "saspha": {
            "short_description": "Stop and Start PowerHA",
            "group": "My-IT-Group"
        },
        "uv": {
            "short_description": "Upgrade Vormetric",
            "group": "Infosec-IT-Group"
        },
        "uc": {
            "short_description": "Upgrade Centrify",
            "group": "My-IT-Group"
        },
        "rj5": {
            "short_description": "Remediate Java 5",
            "group": "My-IT-Group"
        },
        "rj6": {
            "short_description": "Remediate Java 6",
            "group": "My-IT-Group"
        },
        "uaos": {
            "short_description": "Upgrade Server OS",
            "group": "My-IT-Group"
        }
    }
    # set supported vers vars
    supported_os = ["7.4", latest_serv_os]
    supported_java7 = ["Java8"]
    supported_java8 = ["Java7"]
    unsupported_java5 = ["Java5"]
    unsupported_java6 = ["Java6"]
    supported_vormetric = ["X.2"]
    unsupported_vormetric = ["X.1"]
    supported_centrify = ["X.5"]
    unsupported_centrify = ["X.1", "X.2", "X.3", "X.4"]
    supported_oracle = ["yes_oracle"]
    unsupported_oracle = ["no_oracle"]
    supported_db2 = ["yes_db2"]
    unsupported_db2 = ["no_db2"]
    supported_powerha = ["yes_powerha"]
    unsupported_powerha = ["no_powerha"]
user_def = user_def_vars()

# set snow connection
def set_snow_conn():
    # initialize array
    snow_conf = {}
    # read csv
    if form.testing == "Yes":
        snow_conf_file = open(user_def.snow_test_conf, 'r')
    else:
        snow_conf_file = open(user_def.snow_prod_conf, 'r')
    snow_conf_file_reader = csv.reader(snow_conf_file)
    for row in snow_conf_file_reader:
        snow_conf = {
            'instance': row[0],
            'user': row[1],
            'password': row[2],
            }
    snow_conn = pysnow.Client(instance=snow_conf['instance'], user=snow_conf['user'], password=snow_conf['password'])
    return snow_conn
snow_conn = set_snow_conn()

# set upgrade inventory dictionary
def set_easy_upgrade_dict(merged_csv_file):
    # initialize array
    easy_upgrade_dict = {}
    # read csv
    open_merged_csv_file = open(merged_csv_file, 'r')
    merged_csv_file_reader = csv.reader(open_merged_csv_file)
    for row in merged_csv_file_reader:
        if row[1] == user_def.cust_name:
            easy_upgrade_dict[row[0]] = {
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
                'snow_sys_id': row[23]
                }
    return easy_upgrade_dict
easy_upgrade_dict = set_easy_upgrade_dict(user_def.merged_csv_file)

# set environments to upgrade
class env_to_upgrade_vars():
    next_serv_to_upgrade = []
    env_tdc_detected = "n"
    env_prod_detected = "n"
    env_dr_detected = "n"
    next_env_to_upgrade = ""
    env_to_upgrade = []
    for serv, value in easy_upgrade_dict.items():
        if user_def.latest_serv_os not in value['serv_curr_os']:
            env_to_upgrade.append(value['serv_env'])
    for env in env_to_upgrade:
        if env in user_def.tdc_env:
            env_tdc_detected = "y"
        if env in user_def.prod_env:
            env_prod_detected = "y"
        if env in user_def.dr_env:
            env_dr_detected = "y"
    while next_env_to_upgrade == "":
        if env_tdc_detected == "y":
            next_env_to_upgrade = "TDC"
            u_role = "Test"
            for serv, value in easy_upgrade_dict.items():
                if value['serv_env'] in user_def.tdc_env and user_def.latest_serv_os not in value['serv_curr_os']:
                    next_serv_to_upgrade.append(value['serv_name'])
        if env_tdc_detected == "n" and env_prod_detected == "y" and env_prod_detected == "y":
            next_env_to_upgrade = "PROD / DR"
            u_role = "Production"
            for serv, value in easy_upgrade_dict.items():
                if value['serv_env'] in user_def.prod_env or value['serv_env'] in user_def.dr_env and user_def.latest_serv_os not in value['serv_curr_os']:
                    next_serv_to_upgrade.append(value['serv_name'])
        if env_tdc_detected == "n" and env_prod_detected == "y" and env_dr_detected == "n":
            next_env_to_upgrade = "PROD"
            u_role = "Production"
            for serv, value in easy_upgrade_dict.items():
                if value['serv_env'] in user_def.prod_env and user_def.latest_serv_os not in value['serv_curr_os']:
                    next_serv_to_upgrade.append(value['serv_name'])
        if env_tdc_detected == "n" and env_prod_detected == "n" and env_dr_detected == "y":
            next_env_to_upgrade = "DR"
            u_role = "Disaster Recovery"
            for serv, value in easy_upgrade_dict.items():
                if value['serv_env'] in user_def.dr_env and user_def.latest_serv_os not in value['serv_curr_os']:
                    next_serv_to_upgrade.append(value['serv_name'])
env_to_upgrade = env_to_upgrade_vars()

def set_ci_item_sys_id(next_serv_to_upgrade, conn, api_path):
    table = conn.resource(api_path=api_path)
    ci_item_sys_id = []
    for serv_name in next_serv_to_upgrade:
        result = table.get(query={'name': serv_name}, stream=True)
        for record in result.all():
            ci_item_sys_id.append(record['sys_id'])
    return ci_item_sys_id

def set_upgrade_tab():
    upgrade_tab = ""
    for serv, value in easy_upgrade_dict.items():

        # Name
        col_1_span_style = user_def.span_default
        col_1 = user_def.td_tag + col_1_span_style + value['serv_name'] + user_def.close_span + user_def.close_td_tag

        # Current OS
        col_2_span_style = user_def.span_default
        col_2 = user_def.td_tag + col_2_span_style + value['serv_curr_os'] + user_def.close_span + user_def.close_td_tag

        # Environment
        if user_def.latest_serv_os not in value['serv_curr_os']:
            col_3_span_style = user_def.span_default
            col_3_content = value['serv_env']
        else:
            col_3_span_style = user_def.span_green
            col_3_content = "Already Upgraded"
        col_3 = user_def.td_tag + col_3_span_style + col_3_content + user_def.close_span + user_def.close_td_tag

        # Upgrade OS to
        if user_def.latest_serv_os not in value['serv_curr_os']:
            col_4_span_style = user_def.span_default
            col_4_content = user_def.latest_serv_os
        else:
            col_4_span_style = user_def.span_green
            col_4_content = "Already Upgraded"
        col_4 = user_def.td_tag + col_4_span_style + col_4_content + user_def.close_span + user_def.close_td_tag

        # Date / Time
        col_5_span_style = user_def.span_default
        col_5 = user_def.td_tag + col_5_span_style + "" + user_def.close_span + user_def.close_td_tag

        # row
        row = user_def.tr_tag + col_1 + col_2 + col_3 + col_4 + col_5 + user_def.close_tr_tag
        upgrade_tab = upgrade_tab + row

    upgrade_tab = user_def.tab_tag + user_def.tab_upgrade_header + upgrade_tab + user_def.close_tab
    return upgrade_tab

# set serv_group_vars
class serv_group_vars():
    serv_name = easy_upgrade_dict[form.serv_name]['serv_name']
    cust_name = easy_upgrade_dict[form.serv_name]['cust_name'][4:]
    email_to = easy_upgrade_dict[form.serv_name]['lob_email']
    next_env_to_upgrade = env_to_upgrade.next_env_to_upgrade
    next_serv_to_upgrade = env_to_upgrade.next_serv_to_upgrade
    # snow vars
    cmdb_ci = next_serv_to_upgrade[0]
    ci_item_count = len(next_serv_to_upgrade)
    u_role = env_to_upgrade.u_role
    chg_short_description = "Upgrade " + str(ci_item_count) + " " + next_env_to_upgrade + " " + cust_name + " Servers to " + user_def.latest_serv_os + " *Disruptive*"
    chg_description = chg_short_description + "\n\n" + "\n".join(next_serv_to_upgrade)
    ci_item_sys_id = set_ci_item_sys_id(next_serv_to_upgrade, snow_conn, "/table/cmdb_ci_server")
serv_group = serv_group_vars()

def create_chg(chg_network_id, chg_type, chg_start_time, chg_end_time, cmdb_ci, chg_short_description, chg_description, standard_plan, u_test_results, u_related_release, chg_category, chg_subcategory, chg_assignment_group, u_estimated_downtime, u_backout_duration, u_role, conn, api_path):
    table = conn.resource(api_path=api_path)
    create_chg_vars = {
        'assigned_to': chg_network_id,
        'type': chg_type,
        'start_date': chg_start_time,
        'end_date': chg_end_time,
        'cmdb_ci': cmdb_ci,
        'short_description': chg_short_description,
        'description': chg_description,
        'test_plan': standard_plan,
        'u_test_results': u_test_results,
        'change_plan': standard_plan,
        'u_verification_plan': standard_plan,
        'backout_plan': standard_plan,
        'u_related_release': u_related_release,
        'category': chg_category,
        'u_subcategory': chg_subcategory,
        'u_estimated_downtime': u_estimated_downtime,
        'u_backout_duration': u_backout_duration,
        'assignment_group': chg_assignment_group,
        'u_role': u_role
        }
    create_chg_result = table.create(payload=create_chg_vars)
    return create_chg_result.all()
create_chg_result = create_chg(form.chg_network_id, user_def.chg_type, user_def.chg_start_time, user_def.chg_end_time, serv_group.cmdb_ci, serv_group.chg_short_description, serv_group.chg_description, user_def.standard_plan, user_def.u_test_results, user_def.u_related_release, user_def.chg_category, user_def.chg_subcategory, user_def.chg_assignment_group, user_def.u_estimated_downtime, user_def.u_backout_duration, serv_group.u_role, snow_conn,"/table/change_request")

def set_affected_ci(ci_item_sys_id, create_chg_result_sys_id, conn, api_path):
    table = conn.resource(api_path=api_path)
    for sys_id in ci_item_sys_id:
        set_affected_ci_vars = {
            'ci_item': sys_id,
            'task': create_chg_result_sys_id,
        }
        table.create(payload=set_affected_ci_vars)

def set_chg(chg_vars_number, next_env_to_upgrade, conn, api_path):
    table = conn.resource(api_path=api_path)
    if next_env_to_upgrade == "TDC":
        chg_type = "Routine"
    else:
        chg_type = user_def.chg_type
    set_chg_vars = {
        'type': chg_type,
        }
    table.update(query={'number': chg_vars_number}, payload=set_chg_vars)

def create_ctask(sys_id, short_description, description, group, conn, api_path):
    table = conn.resource(api_path=api_path)
    create_ctask_vars = {
        'change_request': sys_id,
        'short_description': short_description,
        'assignment_group': group,
        'description': "\n".join(description),
        'state': "1",
        'expected_start': user_def.chg_start_time,
        'due_date': user_def.chg_end_time,
        'cmdb_ci': serv_group.cmdb_ci,
        }
    table.create(payload=create_ctask_vars)

def set_vers(val):
    vers = []
    for serv, value in easy_upgrade_dict.items():
        if value['serv_name'] in serv_group.next_serv_to_upgrade:
            vers.append(value[val])
    vers = "|".join(vers)
    return vers

def set_vers_serv(val, unsupported_vers):
    vers_serv = []
    for serv, value in easy_upgrade_dict.items():
        if value['serv_name'] in serv_group.next_serv_to_upgrade and any(string in value[val] for string in unsupported_vers):
            vers_serv.append(value['serv_name'])
    return vers_serv

class set_chg_vars():
    number = create_chg_result[0]['number']
    sys_id = create_chg_result[0]['sys_id']
    link = create_chg_result[0]['u_task_url_link']
    review = "Please review <a href=" + '"' + link + '"' + " target=" + '"' + "_blank" + '"' + ">" + number + "</a> scheduled on " + user_def.hum_chg_date + " from " + user_def.hum_start_time + "-" + user_def.hum_end_time + "."
    # set affected ci
    set_affected_ci(serv_group.ci_item_sys_id, sys_id, snow_conn, "/table/task_ci")
    set_chg(number, serv_group.next_env_to_upgrade, snow_conn, "/table/change_request")
    # set ctasks
    oracle_vers = set_vers('is_oracle')
    db2_vers = set_vers('is_db2')
    powerha_vers = set_vers('is_powerha')
    vormetric_vers = set_vers('is_vormetric')
    centrify_vers = set_vers('is_centrify')
    java5_vers = set_vers('is_java5')
    java6_vers = set_vers('is_java6')
    oracle_vers_serv = set_vers_serv('is_oracle', user_def.supported_oracle)
    db2_vers_serv = set_vers_serv('is_db2', user_def.supported_db2)
    powerha_vers_serv = set_vers_serv('is_powerha', user_def.supported_powerha)
    vormetric_vers_serv = set_vers_serv('is_vormetric', user_def.unsupported_vormetric)
    centrify_vers_serv = set_vers_serv('is_centrify', user_def.unsupported_centrify)
    java5_vers_serv = set_vers_serv('is_java5', user_def.unsupported_java5)
    java6_vers_serv = set_vers_serv('is_java6', user_def.unsupported_java6)
chg_vars = set_chg_vars()

def set_ctask(sys_id, curr_vers, unsupported_vers, ctask, description, static):
    if static == "n":
        if any(string in curr_vers for string in unsupported_vers):
            create_ctask(sys_id, user_def.ctask_dict[ctask]['short_description'], description,
                         user_def.ctask_dict[ctask]['group'], snow_conn, "/table/change_task")
    else:
        description = serv_group.next_serv_to_upgrade
        create_ctask(sys_id, user_def.ctask_dict[ctask]['short_description'], description,
                     user_def.ctask_dict[ctask]['group'], snow_conn, "/table/change_task")
    set_ctask_dict = [user_def.ctask_dict[ctask]['short_description'], ", ".join(description), user_def.ctask_dict[ctask]['group']]
    return set_ctask_dict

class set_ctask_result():
    set_ctask_oracle = set_ctask(chg_vars.sys_id, chg_vars.oracle_vers, user_def.supported_oracle, 'iossavdb', chg_vars.oracle_vers_serv, "n")
    set_ctask_db2 = set_ctask(chg_vars.sys_id, chg_vars.db2_vers, user_def.supported_db2, 'ssavdb', chg_vars.db2_vers_serv, "n")
    set_ctask_powerha = set_ctask(chg_vars.sys_id, chg_vars.powerha_vers, user_def.supported_powerha, 'saspha', chg_vars.powerha_vers_serv, "n")
    set_ctask_java5 = set_ctask(chg_vars.sys_id, chg_vars.java5_vers, user_def.unsupported_java5, 'rj5', chg_vars.java5_vers_serv, "n")
    set_ctask_java6 = set_ctask(chg_vars.sys_id, chg_vars.java6_vers, user_def.unsupported_java6, 'rj6', chg_vars.java6_vers_serv, "n")
    set_ctask_vormetric = set_ctask(chg_vars.sys_id, chg_vars.vormetric_vers, user_def.unsupported_vormetric, 'uv', chg_vars.vormetric_vers_serv, "n")
    set_ctask_centrify = set_ctask(chg_vars.sys_id, chg_vars.centrify_vers, user_def.unsupported_centrify, 'uc', chg_vars.centrify_vers_serv, "n")
    set_ctask_sasa = set_ctask(chg_vars.sys_id, "", "", 'sasa', "", "y")
    set_ctask_va = set_ctask(chg_vars.sys_id, "", "", 'va', "", "y")
    set_ctask_uaos = set_ctask(chg_vars.sys_id, "", "", 'uaos', "", "y")
    ctask_tab_dict = {}
    for ctask in set_ctask_oracle, set_ctask_db2, set_ctask_powerha, set_ctask_java5, set_ctask_java6, set_ctask_vormetric, set_ctask_centrify, set_ctask_sasa, set_ctask_va, set_ctask_uaos:
        ctask_tab_dict[ctask[0]] = {
            'task': ctask[0],
            'relevant_serv': ctask[1],
            'assignment_group': ctask[2]
        }
set_ctask_result()


def set_ctask_tab():
    ctask_tab = ""
    for ctask, value in set_ctask_result.ctask_tab_dict.items():
        if value['relevant_serv'] != "":

            # TASK
            col_1_span_style = user_def.span_default
            col_1 = user_def.td_tag + col_1_span_style + value['task'] + user_def.close_span + user_def.close_td_tag

            # Relevant Servers
            col_2_span_style = user_def.span_default
            col_2 = user_def.td_tag + col_2_span_style + value['relevant_serv'] + user_def.close_span + user_def.close_td_tag

            # Assignment Group
            col_3_span_style = user_def.span_default
            col_3 = user_def.td_tag + col_3_span_style + value['assignment_group'] + user_def.close_span + user_def.close_td_tag

            # Assigned to
            col_4_span_style = user_def.span_default
            col_4 = user_def.td_tag + col_4_span_style + "" + user_def.close_span + user_def.close_td_tag

            # row
            row = user_def.tr_tag + col_1 + col_2 + col_3 + col_4 + user_def.close_tr_tag
            ctask_tab = ctask_tab + row

    ctask_tab = user_def.tab_tag + user_def.tab_ctask_header + ctask_tab + user_def.close_tab
    return ctask_tab

upgrade_tab = set_upgrade_tab()
ctask_tab = set_ctask_tab()

print("Content-type:text/html\r\n\r\n")
print("<html>")
print("<head>")
print("<link href=\"http://pathtocss/kw_easy_upgrade.css\" rel=\"stylesheet\">")
print("<title>EasyUpgrade</title>")
print("</head>")
print("<body>")
print("<h1>EasyUpgrade Results</h1>")
print("<div class=\"gray_container\">")
print("<h2>LOB: %s</h2><hr>" % (serv_group.cust_name))
print("<p>%s</p><br>" % (chg_vars.review))
print("<p>From: %s</p>" % (user_def.email_from))
print("<p>To: %s</p>" % (serv_group.email_to))
print("<p>Subject: %s</p><hr>" % (user_def.email_sub))
print("%s" % (user_def.email_greeting))
print("%s" % (upgrade_tab))
print("<p class=\"span_style_red\">We can upgrade all of %s next. Please confirm CTASKs below:</p>" % (serv_group.next_env_to_upgrade))
print("%s" % (ctask_tab))
print("</div>")
print("<br><br><form action=\"http://pathtohtml/kw_easy_upgrade.html\"><input type=\"submit\" value=\"Start Over\" /></form>")
print("<p>Written by Kareem Washington of My-IT-Group</p>")
print("</body>")
print("</html>")