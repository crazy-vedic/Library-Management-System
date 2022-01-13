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
from functools import lru_cache
import keyboard as kb
import csv

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

@lru_cache(maxsize=50)
def loaddata(file='BOOKDATA.csv',pb=None):
    with open(file,encoding='utf-8') as f:
        rows=[]
        reader=csv.reader(f)
        fields=next(reader)
        reader=list(reader)
        quan=len(reader)
        for row in reader:
            try:
                #if reader.index(row)%50==0:#ENABLE PROGRESSBAR
                #    pb['value']=(reader.index(row)/quan)*100
                #    app.update()
                #    pass
                rows.append(row)
            except Exception as e:
                print(e)
                print(row)
    d={}
    for row in rows:
        d[row[0]]={'ID':row[0],'Title':row[1],'Author':row[2],'Rating':row[3],'Date':row[4],'Publisher':row[5]}
    for k,v in list(d.items())[:5]:
        print(k,v)
    return d

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
    global FilterTitle
    global FilterID
    global FilterAuthor
    global FilterRating
    global FilterDate
    global FilterPublisher
    FilterID=StringVar(frame)
    FilterTitle=StringVar(frame)
    FilterAuthor=StringVar(frame)
    FilterRating=StringVar(frame)
    FilterDate=StringVar(frame)
    FilterPublisher=StringVar(frame)
    if STATE!='WELCOME': print(F"User is trying to log in without being on log in page")
    with open('U.P.txt') as f:
        passes=eval(f.read())
    if User.get().strip() in list(passes.keys()):
        if passes[User.get().strip()]==Pass.get().strip():
            pass
        else:
            msgbox=messagebox.showwarning('Incorrect Login Details','The login credentials you entered do not match any user.')
            return
    else:
        msgbox=messagebox.showwarning('Incorrect Login Details','The login credentials you entered do not match any user.')
        return
    STATE="MAIN"
    pb=ttk.Progressbar(frame,orient=HORIZONTAL,length=100,mode='determinate')
    pb.grid(row=4,column=1,sticky=NSEW,columnspan=2,padx=5)
    activedata=loaddata(pb=pb)
    destroyall()
    app.unbind('<Return>')
    app.title("Library Management Tool")
    app.geometry(F"850x520")
    #AdminPEntry.bind('<KeyRelease>',ADMPASS)
    #ID
    Label(frame,text='Book ID :').grid(row=0,column=0)
    Entry(frame,textvariable=FilterID,width=5).grid(row=0,column=1)
    #Title
    Label(frame,text='Title :').grid(row=0,column=2)
    Entry(frame,textvariable=FilterTitle,width=60).grid(row=0,column=3,padx=1)
    #Author
    Label(frame,text='Author :').grid(row=0,column=4)
    Entry(frame,textvariable=FilterAuthor,width=35).grid(row=0,column=5,padx=1,sticky=W)
    #Rating
    Label(frame,text='Rating :').grid(row=1,column=0)
    Entry(frame,textvariable=FilterRating,width=5).grid(row=1,column=1,padx=1,pady=3)
    #Publisher
    Label(frame,text='Publisher :').grid(row=1,column=2)
    Entry(frame,textvariable=FilterPublisher,width=60).grid(row=1,column=3,padx=3)
    #Date
    Label(frame,text='Date :').grid(row=1,column=4)
    Entry(frame,textvariable=FilterDate,width=35).grid(row=1,column=5,padx=1,sticky=W)
    #for child in frame.winfo_children(): child.grid_configure(padx=5, pady=5)
#PASSCHECK=Button(frame,activebackground='#00FFFF',bg='#00FFFF',text="Next",command=MainFrame)
    #TABLE
    table=Frame(frame,bd=4,height=443)
    table.grid(row=2,column=0,sticky=NSEW,columnspan=6,padx=5,pady=4)
    
    TableBBID=Button(table,text='Sno↓↑',width=6).grid(row=0,column=0,sticky=W)
    TableBTitle=Button(table,text='Title',width=50).grid(row=0,column=1,sticky=W)
    TableBAuthor=Button(table,text='Author',width=20).grid(row=0,column=2,sticky=W)
    TableBRating=Button(table,text='Rating',width=6).grid(row=0,column=3,sticky=W)
    TableBPublisher=Button(table,text='Publisher',width=20).grid(row=0,column=4,sticky=W)
    TableBDate=Button(table,text='Date',width=7).grid(row=0,column=5,sticky=W)

    for r in range(1,23):
        exec(F"X{r}0=Entry(table,text=list(activedata.items())[0][1]['ID'],width=7)")
        exec(F"X{r}0.grid(row={r},column=0,sticky=EW)")
        exec(F"X{r}1=Entry(table,text=list(activedata.items())[0][1]['Title'],width=59)")
        exec(F"X{r}1.grid(row={r},column=1,sticky=EW)")
        exec(F"X{r}2=Entry(table,text=list(activedata.items())[0][1]['Author'],width=24)")
        exec(F"X{r}2.grid(row={r},column=2,sticky=EW)")
        exec(F"X{r}3=Entry(table,text=list(activedata.items())[0][1]['Rating'],width=8)")
        exec(F"X{r}3.grid(row={r},column=3,sticky=EW)")
        exec(F"X{r}4=Entry(table,text=list(activedata.items())[0][1]['Publisher'],width=24)")
        exec(F"X{r}4.grid(row={r},column=4,sticky=EW)")
        exec(F"X{r}5=Entry(table,text=list(activedata.items())[0][1]['Date'],width=9)")
        exec(F"X{r}5.grid(row={r},column=5,sticky=EW)")
    Label(table,text='X number of rows present').grid(row=23,column=4,columnspan=2,sticky=W)

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
                if User.get()==User.get().strip() and Pass.get()==Pass.get().strip():
                    passes[str(User.get())]=str(Pass.get())
                else:
                    msgbox=messagebox.showwarning("Credentials Format Error","Please do not leave any spaces at the end or beginning of the User/Name")
                    return
        with open('U.P.txt','w') as f:
            f.write(str(passes))
        RegisterB.configure(bg='green')
        app.after(5000,fixify)
        messagebox.showinfo('User has been added successfully',F"{User.get()} was added as a user to the system.")
        User.set('')
        Pass.set('')
    else:
        msgbox=messagebox.showwarning('Wrong Password','Admin Password entered is wrong.\nPlease contact your admin for the password.')

def fixify(arg=None):
    global RegisterB
    RegisterB.configure(bg='SystemButtonFace')

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
    User.set('Vedic')######################
    Pass.set('Pass')#######################

#app.iconphoto(False, PhotoImage(file=resource_path('icon.png')))

WelcomeFrame()
app.mainloop()
