import email, imaplib, info, os, random, sys, time, winsound

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.color import Color
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from datetime import datetime

scriptdir = os.path.dirname(os.path.realpath(__file__))
options = Options()
options.add_argument("user-data-dir="+scriptdir+"\profile")
#options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.page_load_strategy = "normal"
browser1 = webdriver.Chrome(options=options)
wait = WebDriverWait(browser1, 30)

if len(sys.argv) > 1:
    args = int(sys.argv[1])
else:
    args = 0
            
expectVerification = False            
            
def init():
    browser1.get("https://www.bestbuy.com")
    time.sleep(random.randint(1,3))
    accountbutton = browser1.find_element_by_class_name("account-button")
    accountbutton.click()
    time.sleep(1)
    try:
        browser1.find_element_by_class_name("sign-in-btn")
        browser1.get("https://www.bestbuy.com/identity/global/signin")
        try:
            wait.until(EC.url_contains("https://www.bestbuy.com/identity/signin?"))
            time.sleep(random.randint(1,3))
            login()
        except TimeoutException:
            print("Sign in page timeout")    
    except NoSuchElementException:
        print("Already logged in")   
    time.sleep(random.randint(1,3))
    browser1.get(info.referPages[args])
    
def login():
    try:
        browser1.find_element_by_class_name("cia-signin")
        print("Logging in")
        try:
            emailField = browser1.find_element_by_id("fld-e")
            emailField.send_keys(info.email)
        except NoSuchElementException:
            time.sleep(1)
            
        pwField = browser1.find_element_by_id("fld-p1")
        pwField.send_keys(info.password)
        time.sleep(0.5)	
        loginbutton = browser1.find_element_by_class_name("cia-form__controls__submit")
        loginbutton.click()
    except:
        print("No login prompt")

def buttonCheckLoop():
    inCart = False
    while not inCart:
        error = False
        for sku in skus:  
            color = "#c5cbd5"        
            try:
                item = browser1.find_element_by_xpath(f"//button[contains(@data-sku-id, '{sku}')]")
            except:
                try:
                    item = browser1.find_element_by_xpath(f"//a[contains(@data-sku-id, '{sku}')]") 
                except NoSuchElementException:
                    error = True
                    print(f"Can't find item {sku}")
                    break
            if len(skus) > 1:
                if item is not None:
                    print(f"Found sku: {sku} on page.")
                else:
                    print(f"Can't find item {sku}")
            try:
                color = Color.from_string(item.value_of_css_property("background-color")).hex
            except:
                error = True
                print(f"Error with finding color for item {sku}...continuing...")
                break
            if color != "#c5cbd5":
                inCart = True
                break
            if inCart: break        # we want it to insta-break out of the loop
        if not inCart and not error: 
            # print("Nothing found in stock")
            time.sleep(random.randint(7,10))
            browser1.refresh()
        if error:
            break
        
def cartQueue():
    atcBttn = False
    while not atcBttn:
        try:
            browser1.find_element_by_xpath("//button[@data-sku-id and contains(@class,'btn-primary')]").click()
            # audio alert
            winsound.Beep(1250, 300)
            time.sleep(2)
            
            try:
                # see if we're in queue....
                browser1.find_element_by_xpath("//*[@aria-describedby = 'add-to-cart-wait-overlay']")
                print("In queue")
                expectVerification = True
                yourTurn = False
                while not yourTurn:
                    # check color of add to cart button, breaks out of exception when color changes
                    color = browser1.find_element_by_xpath("//button[@data-sku-id and contains(@class,'btn-primary')]").value_of_css_property("background-color")
                    colorCheck = Color.from_string(color).hex
                    # print(colorCheck)
                    print("Still waiting")
                    time.sleep(0.5)
                    if colorCheck != "#c5cbd5":
                        print("Available!")
                        browser1.find_element_by_xpath("//button[@data-sku-id and contains(@class,'btn-primary')]").click()
                        yourTurn = True
                        try:
                            time.sleep(1)
                            # check if it carted before going to cart
                            browser1.find_element_by_class_name("success")
                            print("Added to cart")
                            atcBttn = True
                            time.sleep(1)
                            checkout()
                        except NoSuchElementException:
                            print("Didn't add to cart")
            except NoSuchElementException:
                try:
                    # check if it carted before going to cart
                    browser1.find_element_by_class_name("success")
                    print("Added to cart")
                    atcBttn = True
                    time.sleep(1)
                    checkout()
                except NoSuchElementException:
                    print("Didn't add to cart")                   
        except NoSuchElementException:
            print("Can't find button")
            break
        except Exception as e:
            print("Error:", e)
        
def checkout():
    print("Going to cart")
    browser1.get("https://www.bestbuy.com/cart")
    
    # click checkout button
    try:
        wait.until(EC.url_to_be("https://www.bestbuy.com/cart"))
        
        # checks if we need to click 'ship to'
        if info.tryToShip:
            time.sleep(1)
            shipHome = browser1.find_element_by_xpath("//*[contains(@id, 'fulfillment-shipping')]") # ship to home ID: id="fulfillment-shipping-4pmjcw2zz24ff-4odjuv524m635"
            if shipHome is not None: 
                print("Selecting ship to home")
                shipHome.click()
        
        time.sleep(1)
        checkout = browser1.find_element_by_xpath("//button[text()='Checkout' and contains(@class,'btn-primary')]")
        print("Clicking Checkout")
        checkout.click()
    except TimeoutException:
        print("Cart page timeout")
        
    # wait for CVV box to appear
    if not info.bbCreditCard:
        time.sleep(1)
        try:
            cvv = browser1.find_element_by_id("credit-card-cvv")
            print('Entering stored CVV')
            cvv.send_keys(info.cvv)    
        except:
            print('No CVV prompt')

    # re-login if prompted (https://www.bestbuy.com/identity/signin?)
    time.sleep(2)	
    if "https://www.bestbuy.com/identity/signin?" in browser1.current_url:
        login()
    else:
        print("No need to log back in")
    
    if expectVerification:
        print("Expecting verification method")
        os.system("pause")
        # choose email for verification code
        # time.sleep(2)    
        # try:    
            # wait.until(EC.url_contains("verification"))
            # try:
                # emailRadio = browser1.find_elements_by_xpath("//input[@type=’radio’]")[1] # second radio button is send to email
                # print("Choosing email for verification code")
                # emailRadio.click()
                # sendCodeButton = browser1.find_element_by_xpath("//button[text()='Continue']")
                # sendCodeButton.click()
            # except NoSuchElementException:
                # print("No verification method prompt")
         # except TimeoutException:
            # print("Verification method form timeout")
            
        # scan email and enter verification code
        # time.sleep(2)
        # try:
            # wait.until(EC.url_contains("verification"))    
            # try:
                # verificationCodeBox = browser1.find_element_by_xpath("//input[@type='text']"))
                # print("Scanning email for verification code")    
                # verificationCodeBox.send_keys(getCode())    
                # continueButton = browser1.find_element_by_xpath("//button[text()='Continue']")
                # continueButton.click()
            # except NoSuchElementException:
                # print("No verification code prompt")
        # except TimeoutException:
            # print("Verification code entry timeout")
    else:
        print("No queue, skipping verification check")
    
    # wait for checkout page
    try:
        wait.until(EC.url_to_be("https://www.bestbuy.com/checkout/r/fast-track"))
        print("On checkout page")
        
        # paypal checkout
        # if info.paypalCheckout:        
            # time.sleep(2)    
            # otherPaymentOptions = browser1.find_element_by_xpath("//a[@data-track = 'other-payment-options-link']")
            # otherPaymentOptions.click()
            # paypalButton = browser1.find_element_by_class_name('payment__paypal-button')
            # paypalButton.click()

        if info.bbCreditCard:
            # choose bb credit card rewards
            time.sleep(1)
            try:
                browser1.find_element_by_class_name("reward-calculator__options")
                print("Selected Best Buy CC reward")        
                rewardchoice = browser1.find_elements_by_xpath("//input[@type='radio' and @name='reward-calculator']")[0] # change to 1 if you want the financing option
                rewardchoice.click()
            except NoSuchElementException:
                print("No Best Buy CC reward options")

        # place order
        # time.sleep(1)
        # placeOrder = browser1.find_element_by_class_name('button__fast-track')
        # placeOrder.click()
        # print('ORDER PLACED! :)')
    
    except TimeoutException:
        print("Checkout page timeout")

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
    imap = imaplib.IMAP4_SSL("imap.gmail.com") 
    imap.login(info.gmail, info.gpassword)   
    have_code = False
    while not have_code:
        imap.select(info.glabel) 
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
                                return verification_code
              
                        except UnicodeEncodeError as e:
                            pass
        else:
            time.sleep(1)

# Actual code run        
init()
time.sleep(random.randint(2,5))

skus = info.skusArray[args]
browser1.get(info.prodPages[args])    

time.sleep(1)
buttonCheckLoop()
cartQueue()