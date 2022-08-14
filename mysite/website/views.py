from django.shortcuts import render
from django.contrib import messages 
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as xlogin
from django.contrib.auth import logout as xlogout

import qrcode 
import hashlib
import cv2 
import time 
import datetime 

def homePage(request):
    if request.user.is_authenticated:
        
        return render(request, "index.html", {"loggedin": True, 'user': str(request.user)})
    else:
        return render(request, "index.html", {"loggedin": False})

def md5hash(email): 
    email = email.strip() 
    email = email.lower() 

    encoded = hashlib.md5(email.encode())

    return encoded.hexdigest()

def register(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        patient = request.POST.get('patient')
        doctor = request.POST.get('doctor')

        if name != "" and email != "" and password != "":
            for user in User.objects.all():
                if user.email == email: 
                    messages.error(request, "Email is already taken.")
                    return HttpResponseRedirect("/registration")
            
            newuser = User.objects.create_user(md5hash(email), email, password) 
            newuser.profile.name = name 

            if patient is not None: newuser.profile.type = 0 
            else: newuser.profile.type = 1

            

            newuser.is_active = True 
            newuser.save()
        else: 
            messages.error(request, "Please ensure to fill out all fields")
    
    return render(request, "pages/register.html")

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=md5hash(email), password=password)

        if user is not None:
            xlogin(request, user)
            return render(request, "index.html", {"loggedin": True, 'user': str(request.user)})
        else:
            messages.error(request, 'Username or Password incorrect')
    
    return render(request, "pages/login.html")

def logout(request):
    xlogout(request)
    return HttpResponseRedirect("/")

def dashboard(request):
    if request.user.is_authenticated:
        request.user.profile.history = sorted(request.user.profile.history,key=lambda x: (x[1]))
        if request.user.profile.type == 1: 
            if request.method == "POST":
                
                if 'patient' in request.POST: 
                    patient = request.POST["patient"]
                    patientuser = User.objects.get(username=md5hash(patient))
                    temppatient = patientuser
                    
                else: 
                    patient = "" 

                if 'notes' in request.POST:
                    notes = request.POST['notes']
                else:
                    notes = None
                
                if notes is not None:
                    

                    img = qrcode.make(notes)
                    img.save('website/qrcodes/sample.png')
                    
                    return render(request, "pages/docdashboard.html", {"patient": temppatient, "isret": True, "notes": notes, "notesb":True}) 

                else:
                    return render(request, "pages/docdashboard.html", {"patient": temppatient, "isret": True}) 
            else: 
                return render(request, "pages/docdashboard.html")
        else: 
            
            history = request.user.profile.history;

            hdata = [0]*12; hlabels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] 
            for entry in history: 
                date = str(entry[1]).split("-") 
                m = int(date[1]) - 1  
                hdata[m] += 1

            if request.method == "POST":
                if 'fullname' in request.POST and request.POST["fullname"] != '': 
                    fullname = request.POST["fullname"] 
                    request.user.profile.name = fullname 
                    request.user.save()

                if 'height' in request.POST and request.POST["height"] != '': 
                    request.user.profile.height = request.POST["height"] 
                    request.user.save()

                if 'weight' in request.POST and request.POST["weight"] != '': 
                    request.user.profile.weight = request.POST["weight"] 
                    request.user.save()
                
                if 'allergy' in request.POST and request.POST["allergy"] != '': 
                    request.user.profile.allergies.append(request.POST["allergy"] + ",") 
                    request.user.save()
                
                if 'medication' in request.POST and request.POST["medication"] != '': 
                    request.user.profile.medications.append(request.POST["medication"] + ",") 
                    request.user.save()
                
                if 'diagnosis' in request.POST and request.POST["diagnosis"] != '': 
                    request.user.profile.diagnoses.append(request.POST["diagnosis"] + ",") 
                    request.user.save()

                if 'street' in request.POST and request.POST["street"] != '': 
                    request.user.profile.address = request.POST["street"] 
                    request.user.save()
                
                if 'city' in request.POST and request.POST["city"] != '': 
                    request.user.profile.city = request.POST["city"] 
                    request.user.save()
                
                if 'province' in request.POST and request.POST["province"] != '': 
                    request.user.profile.province = request.POST["province"] 
                    request.user.save()
                
                if 'postalcode' in request.POST and request.POST["postalcode"] != '': 
                    request.user.profile.postalcode = request.POST["postalcode"] 
                    request.user.save()

                if 'qr' in request.POST:
                    img = cv2.imread('website/qrcodes/sample.png')
                    detector = cv2.QRCodeDetector()
                    data, vertices_array, binary_qrcode = detector.detectAndDecode(img)
                    request.user.profile.history.append([int(time.time()), datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'), data])
                    request.user.save()
                
                if 'submit' in request.POST:
                    udate = request.POST["date"] 
                    notesc = request.POST["notesc"] 

                    dt = datetime.datetime.strptime(udate,"%d/%m/%Y")
                    timestamp = int(dt.timestamp())

                    request.user.profile.history.append([timestamp, datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S'), notesc ])
                    request.user.save()

                if 'date' in request.POST and 'aptype' in request.POST: 
                    newapdate = request.POST["date"] 
                    newaptype = request.POST['aptype'] 

                    t = newapdate.split('/')
                    s = t[1] + "/" +t[0] + "/" +t[2]
                    dt = int(datetime.datetime.strptime(s,"%d/%m/%Y").timestamp()) 

                    request.user.profile.upcoming.append([dt, newapdate, newaptype])
                    request.user.save() 

                return HttpResponseRedirect('/dashboard')
            else:
                return render(request, "pages/patdashboard.html", {'hlabels':hlabels, 'hdata':hdata})
    else: 
        return HttpResponseRedirect("/login")