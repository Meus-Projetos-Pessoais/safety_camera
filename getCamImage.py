# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 13:37:54 2019

@author: aw1001
"""
from datetime import datetime
import time
import cv2
import base64
import bd_connect

def get_image(execution = 5):
    mycursor = bd_connect.mydb.cursor()
    i=0
    sql = "SELECT * from cameras"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    sql = "INSERT INTO images (idcamera, raw_image, acquisition_time,status) VALUES (%s, %s, %s, %s)"
    stime= time.time()
    cam_lst = []
    for cam_inf in myresult:
        cam_lst.append([cam_inf[0],cv2.VideoCapture(cam_inf[3])])
    print("Camera connection time: " + str(time.time()-stime)) 
    stime=time.time()
    
    while execution:
        ltime=time.time()
        i+=1
        if ltime-stime >= 3:
            stime=ltime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for cam_inf,cam in cam_lst:  
                retval, img = cam.read()
                if retval:
                    img = cv2.resize(img,(1920,1080),interpolation = cv2.INTER_AREA)
                    retval, img = cv2.imencode('.jpg', img)
                    img = base64.b64encode(img)
                    lst = (cam_inf,img.decode('utf-8'),now,0)
                    mycursor.execute(sql, lst)
            print("Batch image acquisition time: " + str(time.time()-stime))
            execution -= 1
            bd_connect.mydb.commit()
        if i >= 30:
            i=0
            for cam_inf,cam in cam_lst:
                cam.release()        
            for cam_inf in myresult:
                cam_lst.append([cam_inf[0],cv2.VideoCapture(cam_inf[3])])
    print("End acquisition!")       

get_image()    