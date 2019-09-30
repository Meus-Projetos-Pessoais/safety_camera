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

mycursor = bd_connect.mydb.cursor()
sql = "SELECT * from images where status = 5"
mycursor.execute(sql)
myresult = mycursor.fetchall()
i=0
for i,image in enumerate(myresult):  
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stime= time.time()
    decoded_img = base64.b64decode(image[7])
    file_bytes = np.asarray(bytearray(decoded_img), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    #print(f"decode bas64 time:{time.time()-stime}")
    anomalies = json.loads(image[5])
    for item in anomalies:
        if "safety" in item:
           continue 
        elif "no" in anomalies[item]["class"]:
            img = cv2.rectangle(img, (anomalies[item]["left"], anomalies[item]["top"]), (anomalies[item]["right"], anomalies[item]["bottom"]), (0,255,0), 1)
    retval, buffer = cv2.imencode('.jpg', img)
    lst = (buffer.tostring(),now,'10',image[0])
    sql = "UPDATE images SET processed_image = %s, update_time = %s, status = %s WHERE idimage = %s"
    mycursor.execute(sql, lst)
bd_connect.mydb.commit()
print(f"{i} images processed. Applications finished!")
