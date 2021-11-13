from os import rename
from django.http.response import HttpResponse
from django.http import FileResponse
from django.shortcuts import redirect, render
from .models import FilesUpload
import os
import io
import base64
import textwrap
import xml.etree.ElementTree as ET
from reportlab.lib.utils import open_and_read, open_and_readlines, open_for_read, open_for_read_by_name
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle,Frame
from reportlab.lib import colors, styles
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.doctemplate import FrameActionFlowable
from reportlab.platypus.flowables import Image, PageBreak
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas, textobject
from reportlab.lib.pagesizes import A4

import glob
from signxml import XMLVerifier, exceptions
import zipfile

import os

import datetime

import pdfplumber


def home(request):
    if request.method=="POST":
        
        try:
            
            file2=request.FILES["file"]
            document= FilesUpload.objects.create(file=file2)
            document.save()
            file_name = str(file2)
            data = reportlab_view(file_name)
            print(data)
            return FileResponse(data[0], as_attachment=True, filename=data[1]+'Aadhar(EKYC).pdf'.format(name=data[1]))
        except exceptions as e :
            print(e)
            return redirect('error')   
    else:
        files = (os.path.join(os.path.abspath('.'), 'media/'))
        for f in os.listdir(files):
            os.remove(os.path.join(files, f))
        print(os.path.join(os.path.abspath('.'), 'media/'))
        return render(request, "index.html")


def error(request): 
    return render(request, 'error.html')


def reportlab_view(file_name):

    content_as_bytes = pdfplumber.open(os.path.join(os.path.abspath('.'), 'media/', file_name))
     
    abc = ''.join(char.get('text') for char in content_as_bytes.pages[0].chars)
    content_as_bytes=base64.b64decode(abc[abc.find('xml-start')+9:abc.rfind('xml-end')])
    xmlwrite = open(os.path.abspath('.')+'/xml.xml', 'wb')
    xmlwrite.write(content_as_bytes)
    xmlwrite.close() 
    try:
        ct=datetime.datetime.now()
        x=ct.strftime("%Y-%m-%d %H:%M:%S")
        XMLVerifier().verify(content_as_bytes, x509_cert=open(os.path.join(os.path.abspath('.'),'uidai_auth_sign_prod_2023.cer')).read())
        a="Valid Document. Verified on: {time}".format(time=x)
    except:
        a="Invalid Document"

    #Text wrap to wrap it in the pdf document
    XML_readable=textwrap.wrap(str(content_as_bytes),width=147)
    #tree_path = os.path.abspath('.')+'/media/'+file_name
    #print(tree_path)
    tree_path = os.path.abspath('.')+'/xml.xml'
    print(tree_path)
    tree= ET.parse(source=tree_path)
    root= tree.getroot()      

    buffer = io.BytesIO()
    c= canvas.Canvas(buffer,pagesize=A4)

    for refrenceid in root.iter('OfflinePaperlessKyc'):
        id= refrenceid.get('referenceId')
        
    for data in root.iter('Poi'):
        dob = data.get('dob')
        gender = data.get('gender')
        name= data.get('name')

    for data in root.iter('Poa'):
        father = data.get('careof')
        country = data.get('country')
        dist = data.get('dist')
        address1= data.get('house')
        address2= data.get('landmark')
        address3= data.get('loc')
        address4=data.get('street')
        pincode=data.get('pc')
        postoffice=data.get('po')
        subdist=data.get('subdist')
        vtc=data.get('vtc')
        state=data.get('state')

    for data in root.iter('Pht'):
            photo=data.text
            photo64 = bytes(photo, 'utf-8')
            decodeit = open((os.path.abspath('.')+'/media/'+'{name}.jpeg').format(name=name), 'wb')
            decodeit.write(base64.b64decode((photo64)))
            decodeit.close()
    
    #border
    c.setStrokeColorRGB(0.686,0.152,0.372)#for outer rect
    c.setFillColorRGB(0.686,0.152,0.372)#for outer rect

    #Outer Rect
    c.rect(0,715,595,715,fill=1)
    c.setStrokeColorRGB(0,0,0)
    c.rect(473,507,94,97)
    
    #personal Information
    c.setFont("Helvetica",size=20)
    c.drawString(165,670,"PERSONAL INFORMATION")
    #Underline
    c.setStrokeColorRGB(0.686,0.152,0.372)#for line below text
    c.line(156,667,421,667)#for line below text

    #Title
    c.setFillColorRGB(1,1,1)#for string
    c.setFont("Helvetica",size=30)
    #c.setFillColorRGB(0.686,0.152,0.372)
    c.drawString(140,785,"AXIS FINANCE LIMITED")

    #personal info
    #Outer Rect
    c.setStrokeColorRGB(0.5,0.5,0.5)#for outer rect
    c.setFillColorRGB(0.686,0.152,0.372)#for outer rect
    #Underline
    c.setStrokeColorRGB(1,1,1)#for rect below text
    c.rect(200,735,190,28)#for rect below text
    c.setFillColorRGB(1,1,1)#for string
    c.setFont("Helvetica",size=23)
    c.drawString(210,740,"AADHAR E-KYC")
    c.drawImage(image=(os.path.abspath('.')+'/fileupload/footer.png'),x=0,y=0, width=600,height=80)
    
    #Photo
    c.drawInlineImage(image=(os.path.abspath('.')+'/media/'+'{name}.jpeg').format(name=name), x=475,y=510, width=90,height=90,showBoundary=True)


    
    #Table
    flow_obj=[]
    t=Table([['Reference ID:                                        ',id+'                                            '],['Name:'+name,'Guardian:'+father],['Date of Birth:'+dob,'Gender:'+gender],['Address:',address1+'\n'+address2+'\n'+address3+'\n'+address4],['Pincode:'+pincode,'Postoffice:'+postoffice],['Sub-district:'+ subdist,'VTC Name:'+ vtc],['State:'+ state,'Country:'+ country],['Verification:',a]])
    ts=TableStyle([('GRID',(0,0),(-1,-1),1,colors.black)])
    t.setStyle(ts)   
    flow_obj.append(t)
    frame=Frame(115,460,300,200, rightPadding=40,topPadding=5)
    frame.addFromList(flow_obj,c)

    c.setFillColorRGB(0,0,0)
    c.setStrokeColorRGB(0,0,0)
    c.rect(30,85,550,365)
    c.setFont("Helvetica",size=5.5)
    textobject=c.beginText()
    textobject.setTextOrigin(34,440)    
    textobject.textLines(XML_readable,trim=1)
    c.drawText(textobject) 

    c.showPage() # method causes the canvas to stop drawing on the current page
    c.save() 

    buffer.seek(0)
    print("here")
    return (buffer,name) 
    return FileResponse(buffer, as_attachment=True, filename='{name} Aadhar(EKYC).pdf'.format(name=name))