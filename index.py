from flask import Flask
from fastapi import FastAPI, Request, Depends, BackgroundTasks,Form,Cookie,File, UploadFile,Query,HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates 
import json
from pydantic import BaseModel
from datetime import datetime
import os
import re
import shutil
from main import *
# import tablib
from werkzeug.utils import secure_filename
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from mongoengine import *
from starlette.requests import *
from starlette.responses import *
# from pymsgbox import *
# import tkinter
# from tkinter import messagebox
# import win32api
# import js2py
# import pandas
# import ctypes
import os.path

login=False
username=None
templates =Jinja2Templates(directory="templates")
app = FastAPI()

DB_URI="mongodb+srv://test:test@cluster0-bhmuu.mongodb.net/test?retryWrites=true&w=majority"
connect(host=DB_URI)

class placement(Document):
    firstname=StringField(required=True)
    lastname=StringField(required=True)
    email=EmailField(unique=True,required=True)
    password=StringField(required=True)
    admin=BooleanField(default=False)
    date_created=DateTimeField(default=datetime.utcnow)
    student=BooleanField(default=False)
    recruiter=BooleanField(default=False)


app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/fonts", StaticFiles(directory="fonts"), name="fonts")
app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/js", StaticFiles(directory="js"), name="js")

@app.get('/upload')
async def m(response: Response,request: Request):
    if(login is True):
        return templates.TemplateResponse("rupload.html",{
                "request":request,
                "message":None
            })
    else:
        return RedirectResponse(url="/login",status_code=302)
@app.get('/')
async def home(response: Response,request: Request):
    print(login)
    if(login is True):
        global username
        print(username)
        print("helllllooooo")
        return templates.TemplateResponse("index.html",{
                "request":request,
                "message":username
            })
    else:
        return RedirectResponse(url="/login",status_code=302)
@app.get('/login')
async def home(response: Response,request: Request):
    return templates.TemplateResponse("login.html",{
                "request":request
                })
@app.get('/signup')
async def home(response: Response,request: Request):
    return templates.TemplateResponse("signup.html",{
            "request":request,
              "email_m":False,
            "pass_m":False
        })
@app.get('/logout')
async def logout(response: Response,request: Request):
    global login
    login=False
    return RedirectResponse(url="/login",status_code=302)
@app.post('/upload')
async def create_upload_file(request: Request,response: Response,file: UploadFile = File(...),rskills: str = Form(None)):
    path="C:\\Users\\User\\Desktop\\Resume-Rater-master\\src\\data\\test"
    global upload_folder
    file_object = file.file
    upload_folder=path
    upload_folder = open(os.path.join(upload_folder, file.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    #print(rskills)
    a="fixed"
    b="C:\\Users\\User\\Desktop\\Resume-Rater-master\\src\\data\\test\\"+file.filename
    if(rskills is not None):
        required=rskills.split(',')
    else:
        required=None
    myset={

    }
    if(required is not None):
        for word in required:
            word=word.strip()
            word=word.lower()
            myset[word]=False
    #print(required)

    #print(b)
    #return RedirectResponse(url="/",status_code=302)
    c="model"
    extension = os.path.splitext(file.filename)[1]
    print(extension)
    if(extension=='.pdf' or extension=='.docx' or extension =='.docx'):
        fdata=res(a,b,c)
        data=jsonable_encoder(fdata[0])
        print(data)
        print(fdata[1])
        y=json.loads(data)
        out_skill=y["Skills"].split(',')
        for word in out_skill:
            word=word.strip()
            word=word.lower()
            rword=word[:len(word)-1]
            if(word in myset):
                myset[word]=True
            if(rword in myset):
                myset[rword]=True
            words=word.split(' ')
            for j in words:
                j=j.strip()
                j=j.lower()
                rj=j[:len(j)-1]
                if(j in myset):
                    myset[j]=True
                if(rj in myset):
                    myset[rj]=True
        
        print(myset)
        d=0
        c=0
        for i,j in myset.items():
            if(j==True):
                d=d+1
            c=c+1
        print(d)
        print(c)
        return templates.TemplateResponse("upload.html",{
                "request":request,
                "rating":fdata[1],
                "y":y,
                "myset":myset,
                "d":d,
                "c":c
            })
    else:
        return templates.TemplateResponse("rupload.html",{
            "request":request,
            "message":1
        })

@app.post('/signup')
async def signup(request: Request,response: Response,fname: str = Form(None),lname: str = Form(None),email: str = Form(None),password: str = Form(None),type1: str= Form(None)):
    fname=fname.lower()
    lname=lname.lower()
    email=email.lower()
    check=placement.objects(email=email)

    if(len(check)!=0):
        #error message
        return templates.TemplateResponse("signup.html",{
            "request":request,
            "email_m":True,
            "pass_m":False
        })

    if re.search("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$",password) ==None:
        #error 
        return templates.TemplateResponse("signup.html",{
            "request":request,
             "email_m":False,
            "pass_m":True
        })
    else:
        inp=placement()
        inp.firstname=fname
        inp.lastname=lname
        inp.email=email
        inp.password=password
        inp.admin=False
        if(type1=="o1"):
            inp.recruiter=True
            inp.student=False
        else:
            inp.student=True
            inp.recruiter=False
        inp.date_created=datetime.utcnow
        inp.save()

        return RedirectResponse(url="/login",status_code=302)

@app.post('/login')
async def login(request: Request,response: Response,password: str = Form(None),email: str = Form(None)):
    email=email.lower()
    valid=placement.objects(email=email)
    if valid is not None:
        valid=valid.get()
    if not placement.objects(email=email):
        #error
        return templates.TemplateResponse("login.html",{
                "request":request,
                "message":True
                })
    elif valid.password!=password:
        #valid=log.objects(username=user).get()
        #error
        return templates.TemplateResponse("login.html",{
                "request":request,
                "message":True
                })
    else:
        global username
        username=valid.firstname
        global login
        login=True
        return RedirectResponse(url="/",status_code=302)


