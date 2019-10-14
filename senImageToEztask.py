# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 13:37:54 2019

@author: aw1001
"""
import time
from datetime import datetime
import cv2
import base64
import bd_connect
import numpy as np
import json
import requests

url_cebrace = "http://sistemas.cebrace.com.br/EzTask.WebAPI/api/ocorrencia/salvar"

url_cebrace =  "http://sistemas.cebrace.com.br/EzTask.WebAPI/api/ocorrencia/updatefoto"

def connect_webservice_cebrace(username, password):
    url_cebrace_connect = "http://sistemas.cebrace.com.br/EzTask.WebAPI/api/token"
    headers_cebrace_connect = { "content-type": "application/x-www-form-urlencoded" }
    data_cebrace_connect = { "grant_type": "password", "username": username, "password": password }
    response_conect = requests.post(url_cebrace_connect, data = data_cebrace_connect, headers = headers_cebrace_connect)
    response_conect_json = response_conect.json()

    return response_conect_json["access_token"], response_conect_json["expires_in"]

access_token, expires_in = connect_webservice_cebrace("KEYRUSAPI", "SW2019")
headers_cebrace = { "content-type": "application/json", "Authorization": ("Bearer " + access_token) }
execution = 5
mycursor = bd_connect.mydb.cursor()
sql = "SELECT * from images where status = '10'"
mycursor.execute(sql)
myresult = mycursor.fetchall()
i=0
for image in myresult:  
    i += 1
    jpg_as_text = image[7]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stime= time.time()
    anomalies = json.loads(image[5])
    anomaly_txt= ""
    for item in anomalies:
        if "safety" in item:
            anomaly_txt += "\nAndando fora da faixa de segurança"
        elif "no helmet" in anomalies[item]["class"]:
            anomaly_txt += "\nFalta de capacete"
        elif "no vest" in anomalies[item]["class"]:
            anomaly_txt += "\nFalta de colete"
    ##### trecho para enviar imagem marcada
    jpg_as_text = base64.b64encode(image[8]).decode('utf-8')
    #####
    data_cebrace = json.dumps({ "anexo": jpg_as_text , "dataInicial": image[2].strftime("%Y-%m-%d %H:%M:%S"), "dataFinal": now, "camera": ("Unidade " + "JCR" + " - Local " + "colocar local" ), "anomalia": anomaly_txt })
    response_cebrace = requests.post(url_cebrace, data = data_cebrace, headers = headers_cebrace)
#    print(response_cebrace.status_code)
#    print(response_cebrace.text)
    lst = ('15',response_cebrace.text,image[0])
    if response_cebrace.status_code == 200:
        sql = "UPDATE images SET status = %s, eztask_return = %s WHERE idimage = %s"
        mycursor.execute(sql, lst)
bd_connect.mydb.commit()
print(f"{i} images processed. Applications finished!")

