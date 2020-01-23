from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import os
import sys
import psutil
import logging
from datetime import datetime
import random


# TODO: Use proxies and add random delays to avoid blocking!

# Specify the details of the movie and theatre and showtime here!

THEATRE = 'tdi moti nagar'
ROW = 'A'
SEAT_NUMBER = '7'
MOVIE = 'Tanhaji: The Unsung Warrior (UA)'
SHOWTIME = '12:50'
DATE = '22'
TYPE = '2D'


REPEAT_TIMING_LIST = [9,10,11,12,13]
REPEAT_TIME = random.choice(REPEAT_TIMING_LIST) * 60

SMALL_SLEEPS_LIST = [1.5, 1.8, 2.2, 2.5, 2.8]


# Restarts the this script after closing the process
def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)


def book_seat():
    seat.click()
    payButton = browser.find_element_by_xpath("//*[@id='btmcntbook']")
    payButton.click()


def stop_program():
    print("Stopping this program...")
    browser.quit()
    exit()


def cancel_booking():
    cancelButton = browser.find_element_by_xpath("//*[@id='dismiss']")
    cancelButton.click()


running = True


option = webdriver.ChromeOptions()
# Does not open a chrome window when using this
# option.add_argument("--headless")
# Disables use of GPU to save memory
# option.add_argument("--disable-gpu")
# Uses the incognito mode for Chrome
option.add_argument("--incognito")

browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)

# Open the below URL
browser.get("https://in.bookmyshow.com/national-capital-region-ncr")
# Wait 20 seconds for page to load
timeout = 60
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='navbar']/div[2]/div/div[2]/div")))
    print("Homepage Loaded")
    searchbox = browser.find_element_by_xpath('//*[@id="input-search-box"]')
    time.sleep(random.choice(SMALL_SLEEPS_LIST))
    searchbox.send_keys(Keys.ENTER)
    time.sleep(random.choice(SMALL_SLEEPS_LIST))
    searchbox.send_keys(THEATRE)
    time.sleep(5)
    searchbox.send_keys(Keys.ENTER)
except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='showEvents']/ul")))
    theatreName = browser.find_element_by_xpath('//h1').text
    print(theatreName,"Loaded!")

except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

dateEle = browser.find_element_by_xpath('//div[@class="date-numeric"]')
curSelectedDate = dateEle.text
if(DATE == curSelectedDate):
    pass
else:
    dateEle = browser.find_element_by_xpath("//*[@id='showDates']//li/a/div[contains(text(),'%s')]"%(DATE))
    time.sleep(random.choice(SMALL_SLEEPS_LIST))
    dateEle.click()
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='showEvents']/ul")))
        theatreName = browser.find_element_by_xpath('//h1').text
        print(theatreName,"Date Changed!")

    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()


showTime = browser.find_element_by_xpath("//*[@id='showEvents']//a[contains(text(),'%s')]//ancestor::div[@class='listing-info']/div[@class='eventInfo'][contains(text(),'%s')]//ancestor::li[@class='list']/div[2]//div[contains(text(),'%s')]/ancestor::a"%(MOVIE,TYPE,SHOWTIME))
if 'data-disabled' in showTime.get_attribute("class"):
    print("Sorry! This showtime is either sold out or not available at the moment!")
    print("Quitting the program...")
    browser.quit()
    exit()

print('Showtime: ', showTime.text, 'selected!')
time.sleep(random.choice(SMALL_SLEEPS_LIST))
browser.execute_script("arguments[0].click();", showTime)

# TODO: For some theatres, terms and conditions is not shown and directly number of seats are chosen, handle that case
acceptButton = browser.find_element_by_xpath("//*[@id='btnPopupAccept']")
time.sleep(random.choice(SMALL_SLEEPS_LIST))
browser.execute_script("arguments[0].click();", acceptButton)
print("Accepted the terms!")

# try:
#     WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='pop_1']")))
#     singleSeat = browser.find_element_by_xpath("//*[@id='pop_1']")
#     time.sleep(random.choice(SMALL_SLEEPS_LIST))
#     singleSeat.click()
#     print("Single Seat Clicked!")
# except TimeoutException:
#     print("Timed out waiting for page to load")
#     browser.quit()
# except NoSuchElementException:
#     print("Unable to locate the number of seat option")
#     stop_program()


proceedToSeats = browser.find_element_by_xpath("//*[@id='proceed-Qty']")
time.sleep(random.choice(SMALL_SLEEPS_LIST))
browser.execute_script("arguments[0].click();", proceedToSeats)
print("Proceed to Seats!")

try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//tbody")))
    print("Seat Chart Loaded")

    seat_xpath = "//*[text()='%s']//parent::td//parent::tr/td[position()=2]/div/a[contains(text(),'%s')]"%(ROW,SEAT_NUMBER)
    seat = browser.find_element_by_xpath(seat_xpath)
    availability = seat.get_attribute("class")
    if "available" in availability:
        # Book the seat
        time.sleep(random.choice(SMALL_SLEEPS_LIST))
        book_seat()
        print(datetime.now())
    elif "blocked" in availability:
        print("Sorry! This seat is already booked! Try another.")
        stop_program()

except TimeoutException:
    print("Timed out waiting for page to load - Seat Chart")
    browser.quit()

except NoSuchElementException:
    print("Unable to locate the given seat - %s %s" % (ROW, SEAT_NUMBER))
    stop_program()


for remaining in range(REPEAT_TIME, 0, -1):
    sys.stdout.write("\r")
    sys.stdout.write("{:2d} seconds remaining.".format(remaining))
    sys.stdout.flush()
    time.sleep(1)

print("\nCancelling Booking!")
cancel_booking()
browser.quit()
restart_program()


# IP 122.161.222.151
# //div[@class="eventInfo"][contains(text(),'3D')]