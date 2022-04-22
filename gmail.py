# modified example from https://www.geeksforgeeks.org/python-fetch-your-gmail-emails-from-a-particular-user/

import email, imaplib, info, os, time, winsound
from ctypes import windll

   
def searchEmails(key, value, imap): 
    result, data = imap.search(None, key, '"{}"'.format(value))
    return data
  
def getEmails(result_bytes, imap):
    msgs = [] 
    for num in result_bytes[0].split():
        typ, data = imap.fetch(num, "(RFC822)")
        msgs.append(data)
    return msgs

def getCode():
    clearClipboard()
    imap = imaplib.IMAP4_SSL("imap.gmail.com") 
    imap.login(info.gmail, info.gpassword)   # set gmail and gpassword in info.py
    have_code = False
    while not have_code:
        imap.select(info.glabel)  # set glabel in info.py (and setup a gmail filter to add the label to just best buy verification emails)
        msgs = getEmails(searchEmails("FROM", "BestBuyInfo@emailinfo.bestbuy.com", imap), imap)

        if msgs:
            for msg in msgs[::-1]: 
                for sent in msg:
                    if type(sent) is tuple: 
              
                        imaptent = str(sent[1], "utf-8") 
                        data = str(imaptent)
              
                        try: 
                            indexstart = data.find("Verification code:")
                            data2 = data[indexstart: len(data)]
                            indexend = data2.find("</span>")
                            data3 = data2[0: indexend]
                            bracketpos = data3.rfind(">")
                            
                            verification_code = data3[bracketpos+1: len(data3)]
                            if verification_code:
                                have_code = True
                                imap.close()
                                winsound.Beep(1250, 300)
                                addToClipboard(verification_code)
                                return verification_code
              
                        except UnicodeEncodeError as e:
                            pass
        else:
            time.sleep(1)

def addToClipboard(text):
    command = "echo " + text.strip() + "| clip"
    os.system(command)

def clearClipboard():
    if windll.user32.OpenClipboard(None):
        windll.user32.EmptyClipboard()
        windll.user32.CloseClipboard()


print("Verification code: " + getCode())
