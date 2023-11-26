# Write
from email.mime.text import MIMEText
import urllib.request
# Read
import requests
import time
import serial
from threading import Thread
from matplotlib import pyplot as plt
import numpy as np
import datetime

import smtplib
import imaplib 
from email.mime.image import MIMEImage 
from email.mime.multipart import MIMEMultipart


PORT = 'COM5'
BAUD_RATE = 9600

CHANNEL_ID = '1905002'
API_KEY_WRITE = 'QWCTXCZOP1J09L4H'
API_KEY_READ = 'XD38JBTOBKGE8GPC'

BASE_URL = 'https://api.thingspeak.com'

WRITE_URL = '{}/update?api_key={}'.format(BASE_URL, API_KEY_WRITE)
READ_CHANNEL_URL = '{}/channels/{}/feeds.json?api_key={}'.format(BASE_URL, CHANNEL_ID, API_KEY_READ)
READ_FIELD1_URL = '{}/channels/{}/fields/{}.json?api_key={}&results={}'.format(BASE_URL, CHANNEL_ID, 1, API_KEY_READ, 30)
READ_FIELD2_URL = '{}/channels/{}/fields/{}.json?api_key={}&results={}'.format(BASE_URL, CHANNEL_ID, 2, API_KEY_READ, 30)
READ_FIELD3_URL = '{}/channels/{}/fields/{}.json?api_key={}&results={}'.format(BASE_URL, CHANNEL_ID, 3, API_KEY_READ, 30)

temp    = requests.get(READ_FIELD1_URL)
illum   = requests.get(READ_FIELD2_URL)
motion  = requests.get(READ_FIELD3_URL)
dataJsonT = temp.json()
dataJsonI = illum.json()
dataJsonM = motion.json()

feeds       = dataJsonT["feeds"]
temperature = []
for x in feeds:
    x =  float(x["field1"])
    temperature.append(x)

feeds_illum  = dataJsonI["feeds"]
illumination = []
for x in feeds_illum:
    x =  float(x["field2"])
    illumination.append(x)

feeds_motion = dataJsonM["feeds"]
motion = []
for x in feeds_motion:
    x =  float(x["field3"])
    motion.append(x)
    

def checkMail(mail, serialCommunication):
    email.select("inbox")
    
    while True:
        retcode, response              = email.search(None, '(SUBJECT "SEND REPORT" UNSEEN)')
        retcode, responseTurnOnLight   = email.search(None, '(SUBJECT "LIGHT ON" UNSEEN)')
        retcode, responseTurnOffLight  = email.search(None, '(SUBJECT "LIGHT OFF" UNSEEN)')
        retcode, responseTurnOnHeater  = email.search(None, '(SUBJECT "HEATING ON" UNSEEN)')
        retcode, responseTurnOffHeater = email.search(None, '(SUBJECT "HEATING OFF" UNSEEN)')
        retcode, responseTurnOnCooler  = email.search(None, '(SUBJECT "COOLER ON" UNSEEN)')
        retcode, responseTurnOffCooler = email.search(None, '(SUBJECT "COOLER OFF" UNSEEN)')
        
        if len(response[0]) > 0:
            emailIds = response[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

            sendReport()
        if len(responseTurnOnLight[0]) > 0:
            text = "Lights On"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseTurnOnLight[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
        
        if len(responseTurnOffLight[0]) > 0:
            text = "Lights Off"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseTurnOffLight[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
        
        if len(responseTurnOnHeater[0]) > 0:
            text = "Heater On"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseTurnOnHeater[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
        
        if len(responseTurnOffHeater[0]) > 0:
            text = "Heater Off"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseTurnOffHeater[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
        
        if len(responseTurnOnCooler[0]) > 0:
            text = "Cooler On"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseTurnOnLight[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
        
        if len(responseTurnOffCooler[0]) > 0:
            text = "Cooler Off"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseTurnOffLight[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
                
def sendReport():
    
    message = MIMEMultipart()
    message['Subject'] = 'Daily Report from our Arduino'
    
    plt.ioff()
    x   = np.linspace(0,23,(10*4))
    fig = plt.figure()
    plt.title("Daily temperature")
    plt.xlabel("Hours")
    plt.ylabel("Temperature (°C)")
    plt.plot(x, temperature)
    fileName = 'report-temperature-{}.png'.format(datetime.date.today())
    plt.savefig('D:Stefan\\Edumucation\\University\\IV Year\\IoT\\Final Exam\\Reports\\' + fileName)
   
    tempGraph    = open('D:Stefan\\Edumucation\\University\\IV Year\\IoT\\Final Exam\\Reports\\' + fileName, 'rb')
    msgTempGraph = MIMEImage(tempGraph.read()) #to add image at our attachment
    tempGraph.close()
    message.attach(msgTempGraph)
    
    IllumGraph    = open('D:Stefan\\Edumucation\\University\\IV Year\\IoT\\Final Exam\\Reports\\' + fileName, 'rb')
    msgIllumGraph = MIMEImage(IllumGraph.read())
    IllumGraph.close()
    message.attach(msgIllumGraph)
    
    plt.ioff()
    x   = np.linspace(0,23,(10*3))
    fig = plt.figure()
    plt.title("Daily Illumiantion")
    plt.xlabel("Hours")
    plt.ylabel("Illumination (%)")
    plt.plot(x, illumination)
    fileName = 'report-illumination-{}.png'.format(datetime.date.today())
    plt.savefig('D:Stefan\\Edumucation\\University\\IV Year\\IoT\\Final Exam\\Reports\\' + fileName)
    

    MotionGraph    = open('D:Stefan\\Edumucation\\University\\IV Year\\IoT\\Final Exam\\Reports\\' + fileName, 'rb')
    msgMotionGraph = MIMEImage(MotionGraph.read())
    MotionGraph.close()
    message.attach(msgMotionGraph)
    
    plt.ioff()
    x   = np.linspace(0,23,(10*3))
    fig = plt.figure()
    plt.title("Daily motion detected")
    plt.xlabel("Hours")
    plt.ylabel("Times")
    plt.plot(x, motion)
    fileName = 'report-motion-{}.png'.format(datetime.date.today())
    plt.savefig('D:Stefan\\Edumucation\\University\\IV Year\\IoT\\Final Exam\\Reports\\' + fileName)
    
    
    message.preamble = '=========================================='

    htmlText = """\
        <html>
            <head></head>
            <body>
                <h1>Daily report on {}</h1>
                <p>
                    The minimum daily temperature was: <strong>{:.2f}</strong> C and the maximum was <strong>{:.2f}</strong> C and the average daily was <strong>{:.2f}</strong> C.
                </p>
                <p>
                    The minimum daily illumination was: <strong>{:.2f}</strong>  and the maximum was <strong>{:.2f}</strong> and the average daily was <strong>{:.2f}</strong> .
                </p>
                d<p>
                    The number of movements detected were: <strong>{:.2f}</strong> .
                </p>
            </body>
        </html>
        
        
            
    
    """.format(datetime.date.today(),np.min(temperature), np.max(temperature), np.average(temperature), np.min(illumination), np.max(illumination), np.average(illumination), len(motion))

    mimeText = MIMEText(htmlText, 'html')
    message.attach(mimeText)
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    r = server.login('singidunumrpi@gmail.com','holvwfhucmhuybje')
    r = server.sendmail('singidunumrpi@gmail.com', 'singidunumrpi@gmail.com', message.as_string())
    server.quit()
    print('Report sent!')


def processData(data):
    processedData = {}
    dataList = data.split()
    
    if len(dataList) >= 3:
        processedData["temp_value"]     = dataList[0]
        processedData["illum_value"]    = dataList[1]
        processedData["motion_value"]   = dataList[2]
        sendTS(processedData)

def sendTS(data):
    
    resp = urllib.request.urlopen("{}&field1={}&field2={}&field3={}".format(WRITE_URL, data["temp_value"], data["illum_value"], data["motion_value"]))

def recieve(serialCom):
    receivedMessage = ""
    while True:
        if serialCom.in_waiting > 0:
            receivedMessage = serialCom.read(size=serialCom.in_waiting).decode('ascii')
            print(receivedMessage)
            processData(receivedMessage)
            
        time.sleep(5)

serialCommuncation = serial.Serial(PORT, BAUD_RATE)

email = imaplib.IMAP4_SSL('imap.gmail.com')
email.login('singidunumrpi@gmail.com','holvwfhucmhuybje')

checkEmailThread = Thread(target = checkMail, args = (email, serialCommuncation,))
checkEmailThread.start()

receivingThread = Thread(target = recieve, args = (serialCommuncation, ))
receivingThread.start()



