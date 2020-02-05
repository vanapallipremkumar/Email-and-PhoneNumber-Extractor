from tkinter import *
import tkinter as tk
import smtplib
from tkinter import messagebox
import re
import sqlite3

class Mail:
    def __init__(self,mails,phones,fileName):
        self.sentSuccess=False
        self.window=Tk()
        self.allMails=mails
        self.allPhones=phones
        self.fileName=fileName
        self.currentDataClicked=True
        self.choices=("Current Data","Stored Data")
        self.variable=StringVar()
        self.variable.set(self.choices[0])
        self.algoChoice=OptionMenu(self.window,self.variable,*self.choices)
        self.processButton=Button(self.window,relief=tk.GROOVE,
                        text="Selected  "+self.choices[0],command=self.sel,width=23)
        
        self.mag=Label(self.window,text="Enter Magazine Name \n(or)\n Date(DD/MM/YYYY)",font="14",fg="#fff",bg="#000")
        self.magEntry=Entry(self.window,width=25)
        self.senderPL=Label(self.window,text="Password",font="14",fg="#fff",bg="#000")
        self.senderML=Label(self.window,text="Sender Mail",font="14",fg="#fff",bg="#000")
        self.senderPL=Label(self.window,text="Password",font="14",fg="#fff",bg="#000")
        self.senderME=Entry(self.window,width=25)
        self.senderPE=Entry(self.window,show="*",width=25)
        self.receiverML=Label(self.window,text="Receiver Mail",font="14",fg="#fff",bg="#000")
        self.receiverME=Entry(self.window,width=25)
        self.send=Button(self.window,relief=tk.GROOVE,text="Send",command=lambda : self.SendMail())
        
    def CreateGUI(self):
        self.window.title("Mail Windows")
        self.window.geometry('400x450')
        self.window.resizable(0,0)
        self.window.configure(background="#000")

        self.algoChoice.grid(row=0,column=0,padx=10,pady=20,sticky=W)
        self.processButton.grid(row=0,column=1,padx=10,pady=20)
        self.mag.grid(row=1,column=0,padx=10,pady=20,sticky=W)
        self.magEntry.grid(row=1,column=1,padx=10,pady=20)
        self.magEntry.configure(state=DISABLED)

        self.senderML.grid(row=3,column=0,padx=10,pady=20,sticky=W)
        self.senderME.grid(row=3,column=1,padx=10,pady=20)
        self.senderPL.grid(row=4,column=0,padx=10,pady=20,sticky=W)
        self.senderPE.grid(row=4,column=1,padx=10,pady=20)
        self.receiverML.grid(row=5,column=0,padx=10,pady=20,sticky=W)
        self.receiverME.grid(row=5,column=1,padx=10,pady=20)
        self.send.grid(row=6,padx=10,pady=20,sticky='we')
        
        self.window.mainloop()
    def sel(self):
        selection = self.variable.get()
        self.processButton.config(text='Selected '+selection)
        if(selection==self.choices[0]):
            self.processButton.config(text='Selected '+selection)
            self.currentDataClicked=True
            self.magEntry.configure(state=DISABLED)
        else:
            self.currentDataClicked=False
            self.processButton.config(text='Selected '+self.choices[1])
            self.magEntry.configure(state=NORMAL)
    def checkMail(self,mail):
        if not re.match('[^@]+@[^@]+\.[^@]+',mail):
            return False
        return True
    def RetriveData(self):
        if(self.currentDataClicked==False):
            search=self.magEntry.get()
            ret='Date'
            if(search.endswith('.pdf')):
                ret='fileName'
            else:
                if not (re.match('[1-9]+\/[0-9]+\/[0-9]+',search)):
                    return False
                else:
                    search=search.split('/')
                    if(len(search[0])==1):
                        search[0]='0'+search[0]
                    if(len(search[1])==1):
                        search[1]='0'+search[1]
                    search='/'.join(search)
            try:
                c=sqlite3.connect('myData.db')
            except:
                messagebox.showinfo('Database Error',"Unable to Connect Database")
                return
            query='select * from Emails where '+ret+'=\''+search+'\';'
            Dmail=c.execute(query)
            retMails='\nEmails:'
            for i in Dmail:
                retMails=retMails+'\n'+'\t'.join(list(i))
            query='select * from Phones where +'+ret+'=\''+search+'\';'
            Dphones=c.execute(query)
            retPhones='\nPhone Numbers:'
            for i in Dphones:
                retPhones=retPhones+'\n'+'\t'.join(list(i))
            subject='Emails And Phone Numbers from '+search
            content='Subject: {}\n\n{}'.format(subject, retMails+'\n'+retPhones)
            c.close()
            return content
        else:
            messagebox.showinfo('Data Error','Please Proceed with Stored Data')
            return
    def SendMail(self):
        mail=smtplib.SMTP('smtp.gmail.com',587)
        mail.ehlo()
        mail.starttls()
        senderMail=self.senderME.get()
        __senderPass=self.senderPE.get()
        receiverMail=self.receiverME.get()
        if(len(senderMail)==0 or len(receiverMail)==0 or len(__senderPass)==0):
            messagebox.showinfo('Fill All','Fill All Entries')
            return
        if(self.checkMail(senderMail)==False):
            messagebox.showinfo('Mail Error',senderMail+' is Not a Mail')
            return
        if(self.checkMail(receiverMail)==False):
            messagebox.showinfo('Mail Error',receiverMail+' is Not a Mail')
            return
        try:
            mail.login(senderMail,__senderPass)
        except:
            messagebox.showinfo("Login Error","Unable to login Mail\n(or)\nEnable Allow Less Secure Apps in Mail")
        if(self.variable.get()==self.choices[0]):
            if(len(self.allMails)==0 and len(self.allPhones)==0):
                messagebox.showinfo("Nothing Found","No Mails or Phones Numbers Found")
                return
            if(len(self.allMails)==0):
                emailsList="No Emails Found\n"
            else:
                emailsList='Emails\n\t'+'\n\t'.join(self.allMails)
            if(len(self.allPhones)==0):
                phonesList="No Phone Numbers Found\n"
            else:
                phonesList='Phones\n\t'+'\n\t'.join(self.allPhones)
            subject='Emails And Phone Numbers from\t'+self.fileName
            content='Subject: {}\n\n{}'.format(subject, emailsList+'\n'+phonesList)
        else:
            content=self.RetriveData()
            if(content==False):
                messagebox.showinfo("Entry Incorrect","Entered Correct Date")
                return
        try:
            mail.sendmail(senderMail,receiverMail,content)
            messagebox.showinfo("Mail Sent","Mail Sent Successfully")
            self.sentSuccess=True
        except:
            messagebox.showinfo("Mail Not Sent","Unable to  Send Mail\nCheck Connection")
            self.sentSuccess=True
        mail.quit()
        if(self.sentSuccess):
            self.window.destroy()
if __name__=='__main__':
    a=Mail([],[],'')
    a.CreateGUI()
