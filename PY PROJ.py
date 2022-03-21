#NO TIME USE APP.AFTER()
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox,Menu,Checkbutton
import tkinter.scrolledtext as tkst
from functools import lru_cache
import mysql.connector as con
import csv

ADM='ADM'
GLOBALUSER='root'
GLOBALPASS='Vedic'

def stripC(string):
    char_list = []
    for i in range(len(string)):
        if ord(string[i]) in range(65536):
            char_list.append(string[i])
    name = ''.join(char_list)
    return name

def destroyall(arg=None):
    for child in frame.winfo_children(): child.destroy()

@lru_cache(maxsize=50)
def loaddata(file=None,pb=None,raw=False):
    if file==None:
        db=con.connect(user=GLOBALUSER,password=GLOBALPASS,database='library')
        cur=db.cursor()
        try:
            cur.execute(F"select * from library")
        except Exception as e:
            if e.msg=="Table 'library.library' doesn't exist":
                cur.execute("CREATE TABLE library (Sno int NOT NULL PRIMARY KEY UNIQUE,Title varchar(255) NOT NULL,Author varchar(1023) ,Rating float(11, 2) DEFAULT 0,Publication date,Publisher varchar(255),available bool DEFAULT 0)")
                messagebox.showwarning('Missing Table','Table not found, it is being inserted into database "library".\nPlease restart the app.')
                exit()
                return
            else:
                print("There was a breaking error, please contact the developer.")
        alldata,d=cur.fetchall(),[]
        for item in alldata:
            try:
                if pb!=None:
                    if alldata.index(item)%50==0:#ENABLE PROGRESSBAR
                        #print('pb update')
                        pb['value']=(alldata.index(item)/len(alldata))*100
                        app.update()
                d.append({'Sno':str(item[0]),'Title':str(item[1]),'Author':str(item[2]),'Rating':str(item[3]),'Date':str(item[4].strftime("%d/%m/%Y")),'Publisher':str(item[5]),'Available':str(item[6])})
            except Exception as e:
                print(e)
        return d
    else:
        try:
            with open(file,encoding='utf-8') as f:
                rows=[]
                reader=csv.reader(f)
                fields=next(reader)
                reader=list(reader)
                quan=len(reader)
                for row in reader:
                    try:
                        rows.append(row)
                        if pb!=None:
                            if reader.index(row)%200==0:#ENABLE PROGRESSBAR
                                pb['value']=(reader.index(row)/quan)*100
                                app.update()
                    except Exception as e:
                        print(e)
                        print(row)
        except FileNotFoundError as e:
            msgbox=messagebox.showerror('File Not Found',f"'{file}' file was not found. Please make sure it is in the same folder as the application.")
            return 'Not found'
        if not raw:
            d=[]
            for row in rows:
                d.append({'Sno':row[0],'Title':row[1],'Author':row[2],'Rating':row[3],'Date':row[4],'Publisher':row[5],'Available':row[6]})
        else:
            d=rows
        return d

def CSVtoDB(arg=None):
    data=loaddata()
    db=con.connect(user=GLOBALUSER,password=GLOBALPASS,database='library')
    cur=db.cursor()
    for line in data:
        if data.index(line)%100==0:
            print(data.index(line))
        try:
            cur.execute(F"insert into library values({line['Sno']},'{line['Title']}','{line['Author']}',{line['Rating']},'{Datefromdate(line['Date']).strftime('%Y-%m-%d')}','{line['Publisher']}',{line['Available']})")
        except Exception as e:
            print(e)
            print(line)
    db.commit()

app = Tk()
frame=ttk.Frame(app,padding='5 1 5 5')
frame.grid(column=0,row=0,sticky=(N,W,E,S))
app.columnconfigure(0,weight=1)
app.rowconfigure(0,weight=1)

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
    app.geometry(F"250x130")
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

def SettingsFrame(arg=None):
    global STATE
    global ImportVar
    global ExportVar
    global ImportB
    global ExportB
    app.unbind('<Return>')
    app.unbind('<F12>')
    app.bind('<F12>',WelcomeFrame)
    destroyall()
    STATE='SETTINGS'
    app.title(F"Settings")
    app.geometry(F"257x85")
    ImportVar=StringVar()
    ExportVar=StringVar()
    ExportVar.set(f"{datetime.now().strftime('%d%m%y').replace('/','')}_Export_DB.csv")
    ImportB=Button(frame,text="Import DB",command=ImportDB)
    ImportB.grid(column=1,row=0,sticky='E')
    ImportE=Entry(frame,textvariable=ImportVar,width=30)
    ImportE.grid(column=0,row=0)
    ExportB=Button(frame,text="Export DB",command=ExportDB)
    ExportB.grid(column=1,row=1,sticky='E')
    ExportE=Entry(frame,textvariable=ExportVar,width=30)
    ExportE.grid(column=0,row=1)
    FactoryResetB=Button(frame,text='Factory Reset',command=lambda: ImportDB(file='RESETDATA.csv'),width=34,bg='red')
    FactoryResetB.grid(column=0,row=2,columnspan=3,pady=3)

def ImportDB(arg=None,file=None):
    global ImportVar
    data=loaddata(file=str(ImportVar.get()).strip() if file==None else str(file))
    if 'found' in data: return
    db=con.connect(user=GLOBALUSER,password=GLOBALPASS,database='library')
    cur=db.cursor()
    for line in data:
        if data.index(line)%100==0:
            print(data.index(line))
        try:
            cur.execute(F"insert into library values({line['Sno']},'{line['Title']}','{line['Author']}',{line['Rating']},'{Datefromdate(line['Date']).strftime('%Y-%m-%d')}','{line['Publisher']}',{line['Available']})")
        except Exception as e:
            print(e)
            print(line)
    db.commit()
    ImportB.configure(bg='green')
    try:
        app.after(5000,lambda: ImportB.configure(bg='SystemButtonFace'))
    except Exception as e:
        pass

def ExportDB(arg=None):
    global ExportVar
    global totalD
    try:
        if type(totalD)==list: pass
        else: return messagebox.showwarning('Missing data','Data has not been loaded from the db/is missing. Please try logging in to load the data before exporting again.')
    except NameError:
        return messagebox.showwarning('Missing data','Data has not been loaded from the db/is missing. Please try logging in to load the data before exporting again.')
    with open(str(ExportVar.get()).strip(),'w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f)
        writer.writerows([['Sno', 'title', 'authors', 'rating', 'publication', 'publisher', 'Availability']]+[list(item.values()) for item in totalD])
    ExportB.configure(bg='green')
    app.after(5000,lambda: ExportB.configure(bg='SystemButtonFace'))
            
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
    #pb.configure(thickness=5)
    pb.grid(row=3,column=1,sticky=NSEW,columnspan=2,padx=6,pady=5)
    global totalD
    totalD=loaddata(pb=pb)
    destroyall()
    app.unbind('<Return>')
    app.title("Library Management Tool")
    app.geometry(F"912x480")
    #ID
    Label(frame,text='Book ID :').grid(row=0,column=0,sticky=W)
    BK=Entry(frame,textvariable=FilterID,width=5)
    BK.grid(row=0,column=1,sticky=W)
    #Title
    Label(frame,text='Title :').grid(row=0,column=2,sticky=W)
    TITLETEMP=Entry(frame,textvariable=FilterTitle,width=60)
    TITLETEMP.grid(row=0,column=3,padx=1,sticky=W)
    TITLETEMP.bind('<KeyRelease>',updateVData)
    TITLETEMP.focus()
    #Author
    Label(frame,text='Author :').grid(row=0,column=4,sticky=W)
    AUTHORTEMP=Entry(frame,textvariable=FilterAuthor,width=35)
    AUTHORTEMP.grid(row=0,column=5,padx=1,sticky=W)
    AUTHORTEMP.bind('<KeyRelease>',updateVData)
    #Rating
    Label(frame,text='Rating :').grid(row=1,column=0,sticky=W)
    Entry(frame,textvariable=FilterRating,width=5).grid(row=1,column=1,padx=1,pady=3,sticky=W)
    #Publisher
    Label(frame,text='Publisher :').grid(row=1,column=2,sticky=W)
    PUBLISHERTEMP=Entry(frame,textvariable=FilterPublisher,width=60)
    PUBLISHERTEMP.grid(row=1,column=3,padx=1,sticky=W)
    PUBLISHERTEMP.bind('<KeyRelease>',updateVData)
    #Date
    Label(frame,text='Date :').grid(row=1,column=4,sticky=W)
    Entry(frame,textvariable=FilterDate,width=35).grid(row=1,column=5,padx=1,sticky=W)
    #Page Up/Down
    PGUP=Button(frame,text='PgUp',height=1,width=5,command=pgUp).grid(row=0,column=6,sticky=W)
    PGDN=Button(frame,text='PgDn',height=1,width=5,command=pgDown).grid(row=1,column=6,sticky=W)

    #TABLE
    table=Frame(frame,height=443)
    table.grid(row=2,column=0,sticky=NSEW,columnspan=7,padx=5,pady=4)
    #sorters
    global sorters
    TableBSno=Button(table,text='Sno↓',command=lambda: swapState(TableBSno),width=6)
    TableBSno.grid(row=0,column=0,sticky=W)
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
    sorters={'Sno':TableBSno,'Title':TableBTitle,'Author':TableBAuthor,'Rating':TableBRating,'Publisher':TableBPublisher,'Date':TableBDate}
    #Search
    Search=Button(table,text="Import(F12)",font=font.Font(family='Helvetica',name='Settings Font',size=7),height=1,width=10,command=SettingsFrame).grid(row=0,column=6,padx=4,sticky="NSW")

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

        exec(F"SCKB{r}6=IntVar(table,name='CKB{r}')")
        exec(F"global CKB{r}6")
        exec(F"CKB{r}6=Checkbutton(table,text=f'Available',variable=SCKB{r}6,command=lambda: updateAvailability(CKBs[{r}-1]))")
        exec(F"CKB{r}6.grid(row={r},column=6)")
        VISIBLE.append(eval(F"[X{r}0,X{r}1,X{r}2,X{r}3,X{r}4,X{r}5]"))
        exec(F"CKBs.append(SCKB{r}6)")
    global visiblecontent
    visiblecontent=StringVar(table)
    Label(table,textvariable=visiblecontent).grid(row=23,column=4,columnspan=2,sticky='NW')
    global Activedata
    Activedata=totalD
    updateVData()
    app.bind('<Return>',updateVData)
    app.bind('<Prior>',pgUp)
    app.bind('<Shift-Prior>',lambda x: pgUp(pg=10))
    app.bind('<Control-Prior>',lambda x: pgUp(pg=100))
    app.bind('<Next>',pgDown)
    app.bind('<Shift-Next>',lambda x: pgDown(pg=10))
    app.bind('<Control-Next>',lambda x: pgDown(pg=100))

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
    if text.lower()=='delete':
        box.delete('1.0',END)
    else:
        box.insert(INSERT,text)
    box.configure(state='disabled')

def updateAvailability(ckb):
    global VISIBLE
    global CKBs
    global totalD
    global rawd

    db=con.connect(user=GLOBALUSER,password=GLOBALPASS,database='library')
    cur=db.cursor()
    ogshown=[]
    for row in VISIBLE:
        if '\n' in gds(row,squared=False)[0]:
            break
        ogshown.append(list(filter(lambda x: int(x['Sno'])==int(row[0].get('1.0',END)),totalD))[0])#Get original data of everything shown
    idex=int(ckb._name.split('B')[1])
    og=ogshown[int(idex)-1]
    cur.execute(F"update library set available={'1' if og['Available']=='0' else '0'} where Sno={og['Sno']}")
    db.commit()
    return
    '''
    ogshown=[]
    for row in VISIBLE:
        if '\n' in gds(row,squared=False)[0]:
            break
        ogshown.append(list(filter(lambda x: int(x['Sno'])==int(row[0].get('1.0',END)),totalD))[0])#Get original data of everything shown

    else:
        idex=int(ckb._name.split('B')[1])
        og=ogshown[int(idex)-1]
        rawd=loaddata(raw=True)
        try:
            index=rawd.index(list(filter(lambda x: int(og['Sno'])==int(x[0]),rawd))[0])
        except ValueError:
            index=rawd.index(list(filter(lambda x: int(og['Sno'])==int(x[0]),rawd[1:]))[0])
        #print(F"{rawd[index][0]}: {rawd[index][6]}",end='->')
        rawd[index][6]='1' if rawd[index][6]=='0' else '0'
        #print(F"{rawd[index][6]} ({'1' if rawd[index][6]=='0' else '0'})")
        rows=rawd
        if not rows[0]==['bookID','title','authors','average_rating','publication_date','publisher','Availability']: rows.insert(0,['bookID','title','authors','average_rating','publication_date','publisher','Availability'])
        with open('RESETDATA.csv','w',encoding='utf-8',newline='') as f:
            writer=csv.writer(f)
            #print(rows[index])
            writer.writerows(rows)
        totalD=loaddata()
    '''

def updateVData(key=None,filt=True):
    global visiblecontent
    global nav
    global CKBs
    if hasattr(key,'keycode'):
        if not key.keycode in list(range(65,91))+list(range(48,58))+list(range(96,106))+[188,190,192,222,189,8,32,44,36,109,110,187,19,13]:
            return
    if filt: FILTERDATA(so=False,update=False)
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
                CKBs[VISIBLE.index(row)].set(1)
            else:
                CKBs[VISIBLE.index(row)].set(0)
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
        if ''.join([char for char in FilterDate.get() if char.isalpha()])!='':
            messagebox.showerror("Filter Format Error","Date entered is of a bad format")
            return
        try:
            date=Datefromdate(''.join([char for char in FilterDate.get() if char in list(map(str,list(range(0,10))))+['/']]))
            if date==None: return
            data=list(filter(lambda x: date>Datefromdate(x['Date']) if FilterDate.get().startswith('<') or FilterDate.get().endswith('-') or FilterDate.get().startswith('-') else date<Datefromdate(x['Date']) if FilterDate.get().startswith('>') or FilterDate.get().startswith('+') or FilterDate.get().endswith('+') else date==Datefromdate(x['Date'].strip()),data))
        except IndexError as e:
            data=list(filter(lambda x: FilterDate.get().lower() in x['Date'].lower(),data))
    Activedata=list(data)
    if so: sortData('all',update=update)
    else:
        global sorters
        for k,v in sorters.items():
            if not k.startswith('Sno'):
                sorters[k]['text']=''.join(char for char in v['text'] if char.isalpha())

def gds(arg,squared=True):
    lis=[]
    if squared:
        for row in arg:
            lis.append(list(map(lambda x: x.get('1.0',END),row)))
    else:
        lis.append(list(map(lambda x: x.get('1.0',END),arg)))
    return lis

def pgUp(arg=None,pg=1):
    global nav
    listofvis=[ID['Sno'] for ID in Activedata]
    try:
        mini=int(listofvis.index(VISIBLE[0][0].get('1.0',END).strip('\n')))
    except ValueError:
        mini=0
    if mini<=0 or mini-15*int(pg)<0: return
    nav-=15*int(pg)
    updateVData(filt=False)

def pgDown(arg=None,pg=1):
    global nav
    listofvis=[ID['Sno'] for ID in Activedata]
    try:
        mini=int(listofvis.index(VISIBLE[0][0].get('1.0',END).strip('\n')))
    except ValueError:
        mini=0
    try:
        maxi=int(listofvis.index(VISIBLE[-1][0].get('1.0',END).strip('\n')))+1
    except ValueError:
        try:
            maxi=int(listofvis.index(VISIBLE[gds(VISIBLE).index(['\n']*6)-1][0].get('1.0',END).strip('\n')))+1
        except ValueError:
            maxi=0
    #print(F"{mini+15*int(pg)}  {len(Activedata)}")
    if maxi>=len(listofvis) or mini+15*int(pg)>len(Activedata): return
    nav+=15*int(pg)
    updateVData(filt=False)

def Datefromdate(s):
    try:
        if not int(s.split('/')[1]) in list(range(1,13)):
            messagebox.showerror("Filter Format Error","Month must be 1-12")
            return None
    except Exception as e:
        print(e)
        print(s)
    try:
        date=datetime(int(s.split('/')[2]),int(s.split('/')[1]),int(s.split('/')[0]))
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
        try:
            app.after(5000,lambda: RegisterB.configure(bg='SystemButtonFace'))
        except Exception as e:
            pass
        messagebox.showinfo('User has been added successfully',F"{User.get()} was added as a user to the system.")
        User.set('')
        Pass.set('')
    else:
        msgbox=messagebox.showwarning('Wrong Password','Admin Password entered is wrong.\nPlease contact your admin for the password.')

#WELCOME PAGE ON START UP
def WelcomeFrame(arg=None):
    app.title("Login")
    app.geometry(F"205x100")
    app.unbind('<Return>')
    app.bind('<F12>',SettingsFrame)
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
    REGISTER=Button(frame,text='Register',font=font.Font(family='Helvetica',name='Register Button Font',size=8),command=RegisterFrame).grid(row=3,column=1,sticky=NSEW)
    PASSCHECK=Button(frame,activebackground='#00FFFF',bg='#00FFFF',text="Next",command=MainFrame)
    PASSCHECK.grid(row=3,column=2,sticky=NSEW)
    for child in frame.winfo_children():
        child.grid_configure(padx=5, pady=5)
    app.bind('<Return>',MainFrame)
    User.set('Vedic')######################DELETE
    Pass.set('Pass')#######################DELETE

WelcomeFrame()
app.mainloop()
