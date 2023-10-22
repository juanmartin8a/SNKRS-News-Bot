import urllib.request
from urllib.request import urlopen
import json
import os
import time
import bz2
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import itertools
 
MY_ADDRESS = ''
PASSWORD = ''
 
def get_contacts(filename):
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails
 
def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)
 
def untitled():
    url = "https://api.nike.com/product_feed/threads/v2/?anchor=9&count=21&filter=marketplace%28US%29&filter=language%28en%29&filter=upcoming%28true%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29&sort=effectiveStartSellDateAsc&fields=active%2Cid%2ClastFetchTime%2CproductInfo%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent.properties.custom%2CpublishedContent.properties.title"
    inp = urllib.request.urlopen(url)
    
    data = json.load(inp)
    dataList = []
    for i in range(len(data['objects'])):
 
        productImg = data['objects'][i]['productInfo'][0]['imageUrls']['productImageUrl']
        productName = data['objects'][i]['publishedContent']['properties']['title']
        productSlug = data['objects'][i]['publishedContent']['properties']['seo']['slug']
 
        forDataDictionary = {
            'productImg': productImg,
            'productName': productName,
            'productSlug': productSlug
        }
        dataList.append(forDataDictionary)        
 
    newPairExists = False
    if not os.path.exists('snkrs.json'):
        with open('snkrs.json', 'w+') as json_file: 
            dataSnkrs = dataList
            json.dump(dataSnkrs, json_file)
    else:
        dataSnkrsRead = []
        with open('snkrs.json', 'r') as json_file:
            dataSnkrs = json.load(json_file)
            dataSnkrsRead = dataSnkrs
            if dataSnkrs != dataList:
                newPairExists = True
        if newPairExists:
            dataChanged = []
            dataChangedUrls = []
            with open('snkrs.json', 'w+') as json_file: 
                dataSnkrs = dataList
                dataChanged = [x for x in dataSnkrs if x not in dataSnkrsRead]
                for i in range(len(dataChanged)):
                    dataChangedUrls.append('https://www.nike.com/launch/t/' + dataChanged[i]['productSlug'])
 
                json.dump(dataSnkrs, json_file)
            if len(dataChangedUrls) != 0:
                names, emails = get_contacts('contacts.txt') # read contacts
                message_template = read_template('message.txt')
 
                s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
                s.starttls()
                s.login(MY_ADDRESS, PASSWORD)
 
                for name, email in zip(names, emails):
                    msg = MIMEMultipart()       # create a message
 
                    # add in the actual person name to the message template
                    message = message_template.substitute(PERSON_NAME=name.title(), NEW_SNEAKERS = dataChangedUrls)
 
                    # setup the parameters of the message
                    msg['From']=MY_ADDRESS
                    msg['To']=email
                    msg['Subject']="New Sneakers!!"
 
                    # add in the message body
                    msg.attach(MIMEText(message, 'plain'))
 
                    # send the message via the server set up earlier.
                    s.send_message(msg)
                    
                    del msg
                s.quit()
            dataChangedUrls.clear()
            dataList.clear()
 
try: 
    while True:
        untitled()
        time.sleep(10)
except KeyboardInterrupt:
    print('stoped')