#NO TIME USE APP.AFTER()
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox,Menu,Checkbutton
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
    d=[]
    for row in rows:
        d.append({'Sno':row[0],'Title':row[1],'Author':row[2],'Rating':row[3],'Date':row[4],'Publisher':row[5],'Available':row[6]})
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
    global table
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
    global totalD
    totalD=loaddata(pb=pb)
    destroyall()
    app.unbind('<Return>')
    app.title("Library Management Tool")
    app.geometry(F"912x480")
    #AdminPEntry.bind('<KeyRelease>',ADMPASS)
    #ID
    Label(frame,text='Book ID :').grid(row=0,column=0,sticky=W)
    Entry(frame,textvariable=FilterID,width=5).grid(row=0,column=1,sticky=W)
    #Title
    Label(frame,text='Title :').grid(row=0,column=2,sticky=W)
    TITLETEMP=Entry(frame,textvariable=FilterTitle,width=60)
    TITLETEMP.grid(row=0,column=3,padx=1,sticky=W)
    TITLETEMP.focus()
    #Author
    Label(frame,text='Author :').grid(row=0,column=4,sticky=W)
    Entry(frame,textvariable=FilterAuthor,width=35).grid(row=0,column=5,padx=1,sticky=W)
    #Rating
    Label(frame,text='Rating :').grid(row=1,column=0,sticky=W)
    Entry(frame,textvariable=FilterRating,width=5).grid(row=1,column=1,padx=1,pady=3,sticky=W)
    #Publisher
    Label(frame,text='Publisher :').grid(row=1,column=2,sticky=W)
    Entry(frame,textvariable=FilterPublisher,width=60).grid(row=1,column=3,padx=1,sticky=W)
    #Date
    Label(frame,text='Date :').grid(row=1,column=4,sticky=W)
    Entry(frame,textvariable=FilterDate,width=35).grid(row=1,column=5,padx=1,sticky=W)
    #Page Up/Down
    PGUP=Button(frame,text='PgUp',height=1,width=5,command=pgUp).grid(row=0,column=6,sticky=W)
    #PGDN=Button(frame,image=ImageTk.PhotoImage(Image.open('pgdn.png')),height=1,width=4).grid(row=1,column=6,sticky=W)
    PGDN=Button(frame,text='PgDn',height=1,width=5,command=pgDown).grid(row=1,column=6,sticky=W)

    #TABLE
    table=Frame(frame,height=443)
    table.grid(row=2,column=0,sticky=NSEW,columnspan=7,padx=5,pady=4)
    #sorters
    global sorters
    TableBBID=Button(table,text='Sno↓',command=lambda: swapState(TableBBID),width=6)
    TableBBID.grid(row=0,column=0,sticky=W)
    TableBTitle=Button(table,text='Title',width=50,command=lambda: swapState(TableBTitle))
    TableBTitle.grid(row=0,column=1,sticky=W)
    TableBAuthor=Button(table,text='Author',command=lambda: swapState(TableBAuthor),width=20)
    TableBAuthor.grid(row=0,column=2,sticky=W)
    TableBRating=Button(table,text='Rating',command=lambda: swapState(TableBRating),width=5)
    TableBRating.grid(row=0,column=3,sticky=W)
    TableBPublisher=Button(table,text='Publisher',command=lambda: swapState(TableBPublisher),width=20)
    TableBPublisher.grid(row=0,column=4,sticky=W)
    TableBDate=Button(table,text='Date',command=lambda: swapState(TableBDate),width=8)
    TableBDate.grid(row=0,column=5,sticky=W)
    sorters={'Sno':TableBBID,'Title':TableBTitle,'Author':TableBAuthor,'Rating':TableBRating,'Publisher':TableBPublisher,'Date':TableBDate}

    #Search
    Search=Button(table,text="Search",height=1,width=8,command=updateVData).grid(row=0,column=6,padx=4,sticky="NSW")

    global VISIBLE
    VISIBLE=[]
    global CKBs
    CKBs=[]
    for r in range(1,16):
        exec(F"X{r}0=Text(table,height=1,width=6)")
        exec(F"X{r}0.grid(row={r},column=0,sticky='NEW')")
        exec(F"X{r}1=Text(table,height=1,width=40)")
        exec(F"X{r}1.grid(row={r},column=1,sticky='NEW')")
        exec(F"X{r}2=Text(table,height=1,width=15)")
        exec(F"X{r}2.grid(row={r},column=2,sticky='NEW')")
        exec(F"X{r}3=Text(table,height=1,width=5)")
        exec(F"X{r}3.grid(row={r},column=3,sticky='NEW')")
        exec(F"X{r}4=Text(table,height=1,width=15)")
        exec(F"X{r}4.grid(row={r},column=4,sticky='NEW')")
        exec(F"X{r}5=Text(table,height=1,width=8,font=font.Font(family='Helvetica',name='Date Font',size=9))")
        exec(F"X{r}5.grid(row={r},column=5,sticky='NEW')")

        #exec(F"Status{r}6=IntVar()")
        exec(F"StatusCKB{r}6=Checkbutton(table,text=f'Available')")
        #if int(list(totalD.items())[0][1]['Available']):
        #print(int(list(totalD.items())[0][1]['Available']))
        exec(F"StatusCKB{r}6.grid(row={r},column=6)")
        #exec(F"StatusCKB{r}6.select()")
        VISIBLE.append(eval(F"[X{r}0,X{r}1,X{r}2,X{r}3,X{r}4,X{r}5]"))
        exec(F"CKBs.append(StatusCKB{r}6)")
    global visiblecontent
    visiblecontent=StringVar(table)
    Label(table,textvariable=visiblecontent).grid(row=23,column=4,columnspan=2,sticky='NW')
    global Activedata
    Activedata=totalD
    updateVData()
    app.bind('<Return>',updateVData)
    app.bind('<Prior>',pgUp)
    app.bind('<Next>',pgDown)

def swapState(Button):
    if Button['text'].endswith('↑'): Button['text']=f"{Button['text'][:-1]}↓"
    elif Button['text'].endswith('↓'): Button['text']=f"{Button['text'][:-1]}"
    else: Button['text']=f"{Button['text']}↑"
    sortData(Button)

def sortData(button='all',update=True):
    global sorters
    global Activedata
    if button=='all':
        for s,button in sorters.items():
            if button['text'][-1] in ['↓','↑'] and button['text'][:-1] in ['Title','Author','Publisher']:
                Activedata=sorted(Activedata,key=lambda x: x[button['text'][:-1]],reverse=True if button['text'].endswith('↑') else False)
            elif button['text'][-1] in ['↓','↑'] and button['text'][:-1] in ['Sno','Rating']:
                Activedata=sorted(Activedata,key=lambda x: float(x[button['text'][:-1]]),reverse=True if button['text'].endswith('↑') else False)
            elif button['text'][-1] in ['↓','↑'] and button['text'][:-1] in ['Date']:
                Activedata=sorted(Activedata,key=lambda x: Datefromdate(x['Date']),reverse=True if button['text'].endswith('↑') else False)

    if button['text'][-1] in ['↓','↑'] and button['text'][:-1] in ['Title','Author','Publisher']:
        Activedata=sorted(Activedata,key=lambda x: x[button['text'][:-1]],reverse=True if button['text'].endswith('↑') else False)
    elif button['text'][-1] in ['↓','↑'] and button['text'][:-1] in ['Sno','Rating']:
        Activedata=sorted(Activedata,key=lambda x: float(x[button['text'][:-1]]),reverse=True if button['text'].endswith('↑') else False)
    elif button['text'][-1] in ['↓','↑'] and button['text'][:-1] in ['Date']:
        Activedata=sorted(Activedata,key=lambda x: Datefromdate(x['Date']),reverse=True if button['text'].endswith('↑') else False)
    if update: updateVData(filt=False)

def output(box,text):
    box.configure(state='normal')
    if text=='delete':
        box.delete('1.0',END)
    else:
        box.insert(INSERT,text)
    box.configure(state='disabled')

def updateVData(data=None,filt=True):
    global visiblecontent
    global nav
    global CKBs
    if filt: FILTERDATA(so=True,update=False)
    for row in VISIBLE:
        for box in row:
            output(box,'delete')
        for r,col in zip(list(range(0,6)),['Sno','Title','Author','Rating','Publisher','Date']):
            try:
                output(row[r],Activedata[VISIBLE.index(row)+nav][col])
            except IndexError as e:
                continue
            except ValueError as e:
                continue
            except KeyError as e:
                print(r)
                print(Activedata)
                print(col)
                return
        try:
            if int(Activedata[VISIBLE.index(row)+nav]['Available']):
                CKBs[VISIBLE.index(row)].select()
            else:
                CKBs[VISIBLE.index(row)].deselect()
        except IndexError:
            continue
        except ValueError:
            print('valueerror')
            print(Activedata[VISIBLE.index(row)+nav]['Available'])
            
    listofvis=[ID['Sno'] for ID in Activedata]
    try:
        mini=str(int(listofvis.index(VISIBLE[0][0].get('1.0',END).strip('\n')))+1)
    except ValueError:
        mini='0'
    try:
        maxi=str(int(listofvis.index(VISIBLE[-1][0].get('1.0',END).strip('\n')))+1)
    except ValueError:
        try:
            maxi=str(int(listofvis.index(VISIBLE[gds(VISIBLE).index(['\n']*6)-1][0].get('1.0',END).strip('\n')))+1)
        except ValueError:
            maxi='0'
    visiblecontent.set(F"{mini}-{maxi} of {len(Activedata)}")

def FILTERDATA(so=True,update=True):
    global FilterTitle
    global FilterID
    global FilterAuthor
    global FilterRating
    global FilterDate
    global FilterPublisher
    global nav
    global Activedata
    nav=0
    if len(Activedata)!=len(totalD): data=totalD
    else: data=totalD
    if FilterID.get()!='':
        data=list(filter(lambda x: int(x['Sno'])==int(FilterID.get()),data))
    if FilterTitle.get()!='':
        data=list(filter(lambda x: FilterTitle.get().lower() in x['Title'].lower(),data))
    if FilterAuthor.get()!='':
        data=list(filter(lambda x: FilterAuthor.get().lower() in x['Author'].lower(),data))
    if FilterRating.get()!='':
        Rating=float(''.join([char for char in FilterRating.get() if char in list(map(str,list(range(0,10))))+['.']]))
        data=list(filter(lambda x: Rating>float(x['Rating']) if FilterRating.get().startswith('<') or FilterRating.get().endswith('-') or FilterRating.get().startswith('-') else Rating<float(x['Rating']) if FilterRating.get().startswith('>') or FilterRating.get().startswith('+') or FilterRating.get().endswith('+') else Rating==float(x['Rating']),data))
    if FilterPublisher.get()!='':
        data=list(filter(lambda x: FilterPublisher.get().lower() in x['Publisher'].lower(),data))
    if FilterDate.get()!='':
        try:
            date=Datefromdate(''.join([char for char in FilterDate.get() if char in list(map(str,list(range(0,10))))+['/']]))
            if date==None: return
            data=dict(filter(lambda x: date>Datefromdate(x['Date']) if FilterDate.get().startswith('<') or FilterDate.get().endswith('-') or FilterDate.get().startswith('-') else date<Datefromdate(x['Date']) if FilterDate.get().startswith('>') or FilterDate.get().startswith('+') or FilterDate.get().endswith('+') else date==Datefromdate(x['Date'].strip()),data))
        except IndexError as e:
            data=dict(filter(lambda x: FilterDate.get().lower() in x['Date'].lower(),data))
    Activedata=list(data)
    if not so: sortData('all',update=update)
    else:
        global sorters
        for k,v in sorters.items():
            if not k.startswith('Sno'):
                sorters[k]['text']=''.join(char for char in v['text'] if char.isalpha())

def gds(arg):
    lis=[]
    for row in arg:
        lis.append(list(map(lambda x: x.get('1.0',END),row)))
    return lis

def pgUp(arg=None):
    global nav
    listofvis=[ID['Sno'] for ID in Activedata]
    try:
        mini=int(listofvis.index(VISIBLE[0][0].get('1.0',END).strip('\n')))
    except ValueError:
        mini=0
    if mini<=0: return
    nav-=15
    updateVData(filt=False)

def pgDown(arg=None):
    global nav
    listofvis=[ID['Sno'] for ID in Activedata]
    try:
        maxi=int(listofvis.index(VISIBLE[-1][0].get('1.0',END).strip('\n')))
    except ValueError:
        try:
            maxi=int(listofvis.index(VISIBLE[gds(VISIBLE).index(['\n']*6)-1][0].get('1.0',END).strip('\n')))+1
        except ValueError:
            maxi=0
    if maxi>=len(listofvis): return
    nav+=15
    updateVData(filt=False)

def Datefromdate(s):
    try:
        if not int(s.split('/')[0]) in list(range(1,13)):
            messagebox.showerror("Filter Format Error","Month must be 1-12")
            return None
    except Exception as e:
        print(e)
        print(s)
    try:
        date=datetime(int(s.split('/')[2]),int(s.split('/')[0]),int(s.split('/')[1]))
    except ValueError as e:
        print(s)
        return None
    return date

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
