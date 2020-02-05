from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import PyPDF2
from nltk.tokenize import sent_tokenize
import os
import sqlite3
import ntpath
from datetime import date

class GUI:
    def __init__(self):
        self.allMails=set()
        self.allPhones=set()
        self.filePath=""
        self.store=False
        
        self.window=Tk()
        sysWidth=self.window.winfo_screenwidth()
        sysHeight=self.window.winfo_screenheight()
        self.windowWidth=int(sysWidth/2)
        self.windowHeight=int(sysHeight/2)
        
        # Row 1
        self.frame1 = Frame(self.window)
        self.pathDir = Entry(self.frame1)
        self.pathButton = Button(self.frame1,relief=tk.RIDGE,command=self.BrowseFile,
                        text="Browse", width=20,font=('14'))
        #Row 2
        self.frame2 = Frame(self.window)
        self.choices=("Normal","OCR")
        self.variable=StringVar()
        self.variable.set(self.choices[0])
        self.algoChoice=OptionMenu(self.frame2,self.variable,*self.choices)
        self.processButton=Button(self.frame2,relief=tk.GROOVE,
                        text="Proceed",font=('14'),command=self.ExtractData)
        # Name Labels
        self.__epFrame=Frame(self.window)
        self.__emailLabel=Label(self.__epFrame,text="Emails",font=('14'))
        self.__phoneLabel=Label(self.__epFrame,text="Phone Numbers",font=('14'))

        # Row 3
        self.frame3=Frame(self.window,height=int(self.windowHeight))
        self.emailsList=Listbox(self.frame3,
                       height=int(self.windowHeight/15),width=int(self.windowWidth/10))
        self.scrollbarE=Scrollbar(self.frame3,orient="vertical")
        self.phoneList=Listbox(self.frame3,
                      height=int(self.windowHeight/15),width=int(self.windowWidth/10))
        self.scrollbarP=Scrollbar(self.frame3,orient="vertical")
        
        # Row 4
        self.sendDB=Button(self.window,relief=tk.GROOVE,width=int(self.windowWidth/20),
                        text="Store Data",font=('14'),bg="#000",fg="#fff",command=self.__storeData)
        # Row 5
        self.sendMail=Button(self.window,relief=tk.GROOVE,width=int(self.windowWidth/20),
                        text="Send to Mail",font=('14'),bg="#000",fg="#fff",command=self.__sendMail)

    def CreateGUI(self):
        # Window
        self.window.geometry(str(self.windowWidth*2-int(self.windowWidth/2))
                             +"x"+str(self.windowHeight*2-int(self.windowWidth/4)))
        self.window.resizable(0,0)
        self.window.configure(background="#000")
        self.window.option_add("*Font", "verdana")
        # Row 1
        self.frame1.pack(fill=X)
        self.pathDir.pack(side=LEFT,fill=X, padx=5, expand=True)
        self.pathButton.pack(side=LEFT, padx=5, pady=5)

        # Row 2
        self.frame2.pack(fill=X)
        self.algoChoice.pack(side=LEFT,padx=5,pady=5)
        self.processButton.pack(fill=X,padx=5,pady=5)

        # Name Labels
        self.__epFrame.pack(fill='both')
        self.__emailLabel.pack(side=LEFT,padx=20)
        self.__phoneLabel.pack(side=RIGHT,padx=20)

        # Row 3
        self.frame3.pack(fill='both')
        self.emailsList.pack(side=LEFT,padx=5,pady=5,expand=True)
        self.scrollbarE.config(command=self.emailsList.yview)
        self.scrollbarE.pack(side="left", fill="y")
        self.emailsList.config(yscrollcommand=self.scrollbarE.set)
        
        self.phoneList.pack(side=RIGHT,padx=5,pady=5,expand=True)
        self.scrollbarP.config(command=self.phoneList.yview)
        self.scrollbarP.pack(side="right", fill="y")
        self.phoneList.config(yscrollcommand=self.scrollbarP.set)
        
        self.sendDB.pack(side=LEFT,padx=20)
        self.sendMail.pack(side=RIGHT,padx=20)

        self.window.mainloop()

    def BrowseFile(self):
        filename =  filedialog.askopenfilename(initialdir = "~/Desktop",
                                               title = "Select file",
                                               filetypes = (("pdf files","*.pdf"),("all files","*.*")))
        self.pathDir.delete(0,END)
        self.pathDir.insert(0,filename)

    def ExtractData(self):
        self.allMails={}
        self.allPhones={}
        self.store=False
        # Deleting Previous Data
        self.emailsList.delete(0,END)
        self.phoneList.delete(0,END)
        # Checking File exist or not
        file=self.pathDir.get()
        self.filePath=file
        if(len(file)==0):
            messagebox.showinfo("No file","File Not Selected")
            return
        try:
            pdf=open(file,'rb')
        except:
            messagebox.showinfo("No file","File Not existed or May be Deleted")
            return
        option=self.variable.get()
        self.__DisableElements()
        if(option=='Normal'):
            text=self.NormalProcess(pdf)
        else:
        	text=self.OCRProcess(file)
        del pdf
        sentences=list(sent_tokenize(text))
        emails=[]
        phones=[]
        for i in sentences:
            emails.extend(re.findall(r"[A-Za-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+",i))
            phones.extend(re.findall(r'[\+\(]?[1-9]{0,3}[\)]?[0-9 .\-\(\)]{5,15}',i))
        emails=set(emails)
        phones=set(phones)
        if(len(emails)==0 and len(phones)==0):
            messagebox.showinfo("Nothing Found","No Mails and Phone Numbers Found")
        elif(len(emails)==0):
            messagebox.showinfo("No mails","No emails Found")
        elif(len(phones)==0):
            messagebox.showinfo("No Phone Numbers","No Phone Numbers Found")
        # Adding Elements to Emails ListBox
        for i in emails:
            self.emailsList.insert(END,i)
        # Adding Elements to Phone Number ListBox
        for i in phones:
            self.phoneList.insert(END,i)        
        self.allMails=emails
        self.allPhones=phones
        del emails
        del phones
        self.__EnableElements()

    def __EnableElements(self):
        self.pathDir.config(state=NORMAL)
        self.pathButton.config(state=NORMAL)
        self.algoChoice.config(state=NORMAL)
        self.processButton.config(text="Proceed")
        self.processButton.config(state=NORMAL)
        self.sendDB.config(state=NORMAL)
        self.sendMail.config(state=NORMAL)
        
    def __DisableElements(self):
        self.pathDir.config(state=DISABLED)
        self.pathButton.config(state=DISABLED)
        self.algoChoice.config(state=DISABLED)
        self.processButton.config(text="Extracting PDF Data")
        self.processButton.config(state=DISABLED)
        self.sendDB.config(state=DISABLED)
        self.sendMail.config(state=DISABLED)

    def NormalProcess(self,pdf):
        pdfReader=PyPDF2.PdfFileReader(pdf)
        pageCount=pdfReader.numPages
        text=""
        for i in range(pageCount):
            pageData=pdfReader.getPage(i)
            text=text+pageData.extractText()
        return text
    def OCRProcess(self,filePath):
        try:
            from pdf2image import convert_from_path
            import pytesseract
            from PIL import Image
        except:
            messagebox.showinfo('import error',"Error in Importing Following Modules\n pdf2image\npytesseract\nPIL")
            return
        pages = convert_from_path(filePath)
        text=""
        for page in pages:
            page.save('temp.jpg','JPEG')
            img=Image.open('temp.jpg')
            text =text+pytesseract.image_to_string(img)
        os.remove('temp.jpg')
        return text

    def __storeData(self):
        if(self.store==True):
            messagebox.showinfo('Stored',"Data Already Stored")
            return
        self.store=True
        self.__DisableElements()
        try:
            file=open('myData.db','r')
            file.close()
            conn = sqlite3.connect('myData.db')
            conn.isolation_level = None
        except:
            dbFile=open('myData.db','w')
            dbFile.close()
            conn = sqlite3.connect('myData.db')
            conn.isolation_level = None
            emailTable="""CREATE TABLE Emails (
                          fileName TEXT NOT NULL,
                          Date TEXT NOT NULL,
                          Mail TEXT NOT NULL);"""
            phoneTable="""CREATE TABLE Phones (
                          fileName TEXT NOT NULL,
                          Date TEXT NOT NULL,
                          Phone TEXT NOT NULL);"""
            conn.execute(emailTable)
            conn.execute(phoneTable)
        fileName=ntpath.basename(self.filePath)
        Date=date.today().strftime("%d/%m/%Y")
        for mail in self.allMails:
            conn.execute("INSERT INTO Emails VALUES (?,?,?)",[fileName,Date,mail])
            
        for phone in self.allPhones:
            conn.execute("INSERT INTO Phones VALUES (?,?,?)",[fileName,Date,phone])

        conn.close()
        messagebox.showinfo("Done","Successfully Stored")
        self.__EnableElements()

    def __sendMail(self):
        from Mail import Mail
        fileName=ntpath.basename(self.filePath)
        mail=Mail(self.allMails,self.allPhones,fileName)
        mail.CreateGUI()
    
if(__name__=='__main__'):
    main=GUI()
    main.CreateGUI()