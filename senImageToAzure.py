# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 13:37:54 2019

@author: aw1001
"""
import time
import json
import requests
from datetime import datetime
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.webservice import AksWebservice
from azureml.core.workspace import Workspace
import bd_connect
mycursor = bd_connect.mydb.cursor()
    
# Connect to Workspace
def connect_workspace(service_principal_password):
    with open('config/aml_config.json') as f:
        aml_config = json.load(f)

    svc_pr = ServicePrincipalAuthentication(
        tenant_id = aml_config["tenant_id"],
        service_principal_id = aml_config["service_principal_id"],
        service_principal_password = service_principal_password
    )

    ws = Workspace(
            subscription_id = aml_config["subscription_id"],
            resource_group = aml_config["resource_group"],
            workspace_name = aml_config["workspace_name"],
            auth = svc_pr
        )

    return ws

# Connect with WebService using configuration file and Workspace to get URL and key to requisition
def connect_webservice(ws):
    with open('config/aks_config.json') as f:
        aks_config = json.load(f)

    aks_service = AksWebservice(ws, name=aks_config["name"])
    # print(aks_service.state)

    url = aks_service.scoring_uri
    key = aks_service.get_keys()[0]

    return url, key

def connect_webservice_cebrace(password):
    with open('config/ceb_config.json') as f:
        ceb_config = json.load(f)

    url = ceb_config["url_login"]
    header = json.loads(ceb_config["header"])
    data = { "grant_type": "password", "username": ceb_config["username"], "password": password }
    response = requests.post(url, data = data, headers = header)
    response_json = response.json()

    return ceb_config["url_consume"], response_json["access_token"], response_json["expires_in"]



service_principal_password = "e4aEqYiI9eNqoUp6g2TgOjrFVP9U4RJkAxt2gd7SfeY="
ws = connect_workspace(service_principal_password)
url, key = connect_webservice(ws)
print("Workspace connected")

cebrace_api_password = "SW2019"
url_cebrace, access_token, expires_in = connect_webservice_cebrace(cebrace_api_password)

def send_images_to_azure():
    sql = "SELECT * from images WHERE status = 0 ORDER BY acquisition_time DESC LIMIT 14"
    #sql = "SELECT * from images WHERE idimage = 24"
    mycursor.execute(sql)
    images = mycursor.fetchall()
    sql = "SELECT * from cameras "
    mycursor.execute(sql)
    cameras = mycursor.fetchall()
    headers = { 'content-type': 'application/json', 'Authorization': ('Bearer '+ key) }
    json_string = "{"
    json_string += " \"header\": {"
    json_string += " \"url_cebrace\": \"" + url_cebrace + "\","
    json_string += " \"access_token\": \"" + access_token + "\","
    json_string += " \"call_service\": \"false\""
    json_string += " },"
    json_string += " \"body\": {"
    i = 0
    for image in images:
        print(image[0])
        if i == 0:
            json_string += " \"" + str(image[0]) + "\": { \"metadata\": \"" + cameras[image[1]-1][1] + "\", \"safety_regions\": \"" + u'[[[147, 168], [302, 134], [303, 92], [143, 123]]]' + "\", \"image\": \"" +  image[7] + "\" }"
        else:
            json_string += ", \"" + str(image[0]) + "\": { \"metadata\": \"" + cameras[image[1]-1][1] + "\", \"safety_regions\": \"" + u'[[[147, 168], [302, 134], [303, 92], [143, 123]]]' + "\", \"image\": \"" +  image[7] + "\" }"
        i += 1
    json_string += " } }"
    start = time.time()
    response = requests.post(url, data = json_string, headers = headers)
    print (response.status_code)
    print (response.text)
    print(f"Processing time: {time.time() - start}\n")
    if response.text == "No anomalies found" or response.text == "No person found":
        for image in images:
            sql = "DELETE FROM images WHERE idimage = " + str(image[0])
            mycursor.execute(sql)
    else:
        for image in images:
            if response.status_code == 200:
                response_json=json.loads(response.text)
                for item in response_json:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if "message" in item or "status_code" in item:
                        continue
                    if "item" not in str(response_json[item]) and "safety" not in str(response_json[item]):
                        sql = "DELETE FROM images WHERE idimage = " + item
                        mycursor.execute(sql)
                        continue
                    lst = (json.dumps(response_json[item]),now,'5',item)
                    #print(sql)
                    sql = "UPDATE images SET json_returned = %s, update_time = %s, status = %s WHERE idimage = %s"
                    mycursor.execute(sql, lst)
    bd_connect.mydb.commit()
    print(f"{i} Images processed. Application finished!")

for i in range(0,10):
    send_images_to_azure()