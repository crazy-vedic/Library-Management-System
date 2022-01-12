#NO TIME USE APP.AFTER()
import datetime
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import tkinter.scrolledtext as tkst
from PIL import ImageTk,Image
import configparser
import pyautogui as gui
import keyboard as kb

ADM='ADM'

def stripC(string):
    char_list = []
    for i in range(len(string)):
        if ord(string[i]) in range(65536):
            char_list.append(string[i])
    name = ''.join(char_list)
    return name

try:
    config = configparser.ConfigParser()
    config.read('config.ini')
except configparser.ParsingError as e:
    out('p',f'There was an error with your config file.')

def destroyall(arg=None):
    for child in frame.winfo_children(): child.destroy()

def call(link):
    global count
    global start
    if link in list(library.keys()):
        if not time.time()-library[link][1]>30:
            return library[link][0]
    if count == 0:
        start = time.time()
        count=0
    r = requests.post(link)
    #print('new',link)
    library[link]=(r,time.time())
    if r.status_code == 429:
        print(F"You are being rate limited. Please close the app for 60 seconds then try again.")
    elif r.status_code == 401 or r.status_code == 403:
        print(F"You are unauthenticated to get this information from the api, please refresh your key then try again.")
        return
    elif r.status_code == 404:
        print(F"You have recieved a 404 not found error, please speak to a developer and take\
screenshots of the responses by the app to show them, and note what you were doing when this occured.")
        return
    elif r.status_code == 408:
        print(F"Your request timed out, please speak to a developer.")
        return
    count = count + 1
    return r

app = Tk()
frame=ttk.Frame(app,padding='5 1 5 5')
frame.grid(column=0,row=0,sticky=(N,W,E,S))
app.columnconfigure(0,weight=1)
app.rowconfigure(0,weight=1)
#msgbox=messagebox.showwarning('title','message')
def RegisterFrame(arg=None):
    app.unbind('<Return>')
    global STATE
    STATE='REGISTER'
    app.title("Admin Registration Page")
    destroyall()
    global ADMINP
    global AdminPEntry
    global userEntry
    global passEntry
    global RegisterB
    ADMINP=StringVar(frame)
    #RegLabel=Label(frame,text="Register with an Admin Password")
    #RegLabel['font']=font.Font(family='Helvetica',name='Welcome Title Font1',size=20,weight='bold')
    #RegLabel.grid(column=5,row=0)
    AdminPLabel=Label(frame,text="Admin Password").grid(column=2,row=1)
    AdminPEntry=Entry(frame,textvariable=ADMINP,show="*")
    AdminPEntry.bind('<KeyRelease>',ADMPASS)
    AdminPEntry.grid(column=3,row=1)
    userLabel=Label(frame,text='User').grid(column=2,row=2)
    userEntry=Entry(frame,textvariable=User).grid(column=3,row=2)
    passLabel=Label(frame,text='Password').grid(column=2,row=3)
    passEntry=Entry(frame,textvariable=Pass,show="*").grid(column=3,row=3)
    RegisterB=Button(frame,text="Register",command=CheckADM)
    RegisterB.grid(column=3,row=4,sticky=EW)
    BackB=Button(frame,text="Back",command=WelcomeFrame).grid(column=2,row=4,sticky=NSEW)
    app.bind('<Return>',CheckADM)
    for child in frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

def MainFrame(arg=None):
    global STATE
    if STATE!='WELCOME': print(F"User is trying to log in without being on log in page")
    with open('U.P.txt') as f:
        passes=eval(f.read())
    if User.get() in list(passes.keys()):
        if passes[User.get()]==Pass.get():
            pass
        else:
            msgbox=messagebox.showwarning('Incorrect Login Details','The login credentials you entered do not match any user.')
    else:
        msgbox=messagebox.showwarning('Incorrect Login Details','The login credentials you entered do not match any user.')
    STATE="MAIN"
    destroyall()
    app.unbind('<Return>')
    app.title("Library Management Tool")
    app.geometry(F"1000x1000")

def ADMPASS(arg=None):
    global AdminPEntry
    if AdminPEntry.get()==ADM:
        AdminPEntry.configure(bg='green')
    else:
        AdminPEntry.configure(bg='red')

def CheckADM(arg=None):
    global userEntry
    global passEntry
    global RegisterB
    if STATE!='REGISTER':
        print(F"{STATE} User is trying to register without being in register screen")
        msgbox=messagebox.showerror("Please contact the developers","Please contact the developers")
        return
    if ADMINP.get()==ADM:
        with open('U.P.txt','r') as f:
            passes=eval(f.read())
            if User.get() in list(passes.keys()):
                msgbox=messagebox.showwarning("User Already Exists","This user already has a saved profile.\nPlease contact your admin for details")
                return
            else:
                passes[str(User.get())]=str(Pass.get())
        with open('U.P.txt','w') as f:
            f.write(str(passes))
        messagebox.showinfo('User has been added successfully',F"{User.get()} was added as a user to the system.")
        User.set('')
        Pass.set('')
        #RegisterB.configure(bg='green')
        #app.after(5000)
        #RegisterB.configure(bg='SystemButtonFace')
    else:
        msgbox=messagebox.showwarning('Wrong Password','Admin Password entered is wrong.\nPlease contact your admin for the password.')

#WELCOME PAGE ON START UP
def WelcomeFrame(arg=None):
    app.title("Login Page")
    app.unbind('<Return>')
    destroyall()
    global STATE
    global User
    global Pass
    STATE='WELCOME'
    User=StringVar(frame)
    Pass=StringVar(frame)
    userLabel=Label(frame,text='User').grid(row=1,column=1)
    userEntry=Entry(frame,textvariable=User)
    userEntry.focus_set()
    userEntry.grid(row=1,column=2)
    passLabel=Label(frame,text='Password').grid(row=2,column=1)
    userEntry=Entry(frame,textvariable=Pass,show="*").grid(row=2,column=2)
    #Register=ImageTk.PhotoImage(Image.open("register.png"))
    REGISTER=Button(frame,text='Register',font=font.Font(family='Helvetica',name='Register Button Font',size=8),command=RegisterFrame).grid(row=3,column=1,sticky=NSEW)
    #REGISTER['font']=font.Font(family='Helvetica',name='Register Button Font',size=8)
    #REGISTER.grid(row=3,column=1)
    PASSCHECK=Button(frame,activebackground='#00FFFF',bg='#00FFFF',text="Next",command=MainFrame)
    PASSCHECK.grid(row=3,column=2,sticky=NSEW)
    for child in frame.winfo_children():
        child.grid_configure(padx=5, pady=5)
    app.bind('<Return>',MainFrame)

#app.iconphoto(False, PhotoImage(file=resource_path('icon.png')))

WelcomeFrame()
app.mainloop()
