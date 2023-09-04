import sys
if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import threading
import smtplib, ssl
from tkinter import messagebox
from email.message import EmailMessage
import os
import webbrowser

root=tk.Tk()

try:
    driver = webdriver.Firefox(service_log_path=os.devnull)

    notifiedCourses = [] 

    def parseCourses():
        scanLabel.config(text="Scanning under progress...\n You will get a mail whenever a seat is vacant.")
        courses=coursesVar.get()
        coursesArr = courses.split(",")
        
        # Checking courses every minute
        while True:
            message = """ Seats vacant for the following courses: \n\n """
            
            driver.get("https://rds2.northsouth.edu/index.php/common/showofferedcourses") 
            searchBox = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/label/input") 
            select = Select(driver.find_element(By.NAME,'offeredCourseTbl_length'))
            select.select_by_value('100')

            for i in coursesArr:
                searchBox.send_keys(Keys.CONTROL, 'a')
                searchBox.send_keys(Keys.BACKSPACE)
                searchBox.send_keys(i)

                try:
                    for i in range(1,100):
                        try:
                            if int(driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[7]").text)>0 and driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[2]").text+"||"+driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[3]").text not in notifiedCourses:
                                message = message+ f"""
                                Course Name: {driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[2]").text}
                                Section: {driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[3]").text}
                                Faculty: {driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[4]").text}
                                Time: {driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[5]").text}
                                Room: {driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[6]").text}
                                Seats Available: {driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[7]").text}
                                \n
                                """
                                notifiedCourses.append(driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[2]").text+"||"+driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[3]").text)

                            if int(driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[7]").text)==0 and driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[2]").text+"||"+driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[3]").text in notifiedCourses:
                                notifiedCourses.remove(driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[2]").text+"||"+driver.find_element(By.XPATH, "/html/body/div[2]/div/div/table/tbody/tr["+str(i)+"]/td[3]").text)

                        except:
                                pass

                except Exception as e:
                        print(e)
            
            print(notifiedCourses)

            if emailVar.get()=="":
                messagebox.showerror("ERROR", "Please enter your email address")
            else: 
                if message != """ Seats vacant for the following courses: \n\n """:
                    sendSeatNotif(emailVar.get(), message)

            time.sleep(10) # wait 60 seconds before a new iteration of the loop

    def start_combine_in_bg():
        threading.Thread(target=parseCourses).start()

    def sendSeatNotif(recieverEmail, message):
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "nsuadvisingassistant@gmail.com"  # Enter your address 
        message = """\
        """+message

        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = 'SEATS AVAILABLE FOR COURSES!'
        msg['From'] = sender_email
        msg['To'] = recieverEmail
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, "kxyqpgagpyxbrkxi")
            server.send_message(msg)
            server.quit()

    def callback():
        webbrowser.open_new_tab("https://www.facebook.com/abirs.empire17610976/")

    # setting the window size
    root.geometry("700x650")
    root.minsize(700,650)
    root.maxsize(700,650)

    root.title("NSU Advising Assistant v0.1")

    coursesVar=tk.StringVar()
    emailVar = tk.StringVar()

    email_label = tk.Label(root, text = 'Enter your Email Address: ', font=('calibre',10, 'bold'))
    email_entry = tk.Entry(root,textvariable = emailVar, font=('calibre',10,'normal'), width=30)

    name_label = tk.Label(root, text = 'Enter course intials: ', font=('calibre',10, 'bold'))
    name_entry = tk.Entry(root,textvariable = coursesVar, font=('calibre',10,'normal'), width=50)
    name_label2 = tk.Label(root, text = 'You can add more than one courses seperated my a comma. \n E.g. CSE215, CSE231, MAT116', font=('calibre',10, 'bold'))

    sub_btn=tk.Button(root,text = 'Start Scanning', command = start_combine_in_bg)
    stop_btn=tk.Button(root,text = 'Stop Scanning')

    noticeLabel2 = tk.Label(root, text = 'NSU Advising Assistant will notify you whenever seats of your preffered courses gets vacant.\n No more sitting infront of your monitor, No more looking at the RDS all day long. \n Just enter your courses and start scanning. We will email you whenever a seat is vacant', font=('calibre',10, 'bold'))
    noticeLabel = tk.Label(root,fg='red3', text = 'Please DO NOT close the browser window, else the program will not work.', font=('calibre',10, 'bold'))

    scanLabel = tk.Label(root,fg='green', font=('calibre',10, 'bold'))
    creditsLabel = tk.Label(root, text = 'Developed and Maintained by\n Abir Al Mahdi Akhand,\n abir.akhand@northsouth.edu.', font=('calibre',9))
    
    profileLabel = tk.Label(root, fg="blue", text = 'Contact Developer', font=('calibre',9))
    profileLabel.bind("<Button-1>", lambda e: callback())

    email_label.grid(row=0,column=0, padx=100, pady=10)
    email_entry.grid(row=1,column=0)
    name_label.grid(row=2,column=0, padx=100, pady=10)
    name_entry.grid(row=3,column=0)
    name_label2.grid(row=4,column=0, padx=100, pady=10)
    sub_btn.grid(row=5,column=0)
    noticeLabel2.grid(row=7,column=0, pady=20, padx=50)
    noticeLabel.grid(row=9,column=0, pady=20)
    scanLabel.grid(row=8,column=0, pady=20)
    creditsLabel.grid(row=10,column=0, pady=50)
    profileLabel.grid(row=11,column=0, pady=10)
    
    root.mainloop()
    driver.quit()

except:
    messagebox.showerror("ERROR", "Please Install Mozilla Firefox first to run this program. ")
