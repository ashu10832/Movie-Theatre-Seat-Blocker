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


# TODO: Use proxies avoid blocking!

# Specify the details of the movie and theatre and showtime here!
# TODO: Input the details through command line arguments instead of changing the source file everytime
THEATRE = input("Enter Theatre name: ")
MOVIE = input("Enter Movie Name: ")
TYPE = input("Enter type of movie(for example, 2D or 3D): ")
DATE = input("Enter Date (For example 22): ")
SHOWTIME = input("Enter Showtime(for example, 12:50): ")
ROW = input("Enter Row(for example, A): ")
SEAT_NUMBER = input("Enter Seat number(for example, 12): ")


REPEAT_TIMING_LIST = [9,10,11,12,13]
# REPEAT_TIME = random.choice(REPEAT_TIMING_LIST) * 60
REPEAT_TIME = 20
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
    print("Seat blocked at ", datetime.now())
 
def stop_program():
    print("Stopping this program...")
    running = False
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
option.add_argument("--disable-gpu")
# Uses the incognito mode for Chrome
option.add_argument("--incognito")


while(running):
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)

    # Open the below URL
    browser.get("https://in.bookmyshow.com/national-capital-region-ncr")
    # Wait 20 seconds for page to load
    timeout = 60
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='navbar']/div[2]/div/div[2]/div")))
        print("Homepage Loaded!")
        searchbox = browser.find_element_by_xpath('//*[@id="input-search-box"]')
        time.sleep(random.choice(SMALL_SLEEPS_LIST))
        searchbox.send_keys(Keys.ENTER)
        time.sleep(random.choice(SMALL_SLEEPS_LIST))
        searchbox.send_keys(THEATRE)
        time.sleep(5)
        searchbox.send_keys(Keys.ENTER)
    except TimeoutException:
        print("Timed out waiting for page to load")
        stop_program()

    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='showEvents']/ul")))
        theatreName = browser.find_element_by_xpath('//h1').text
        print(theatreName,"Selected!")

    except TimeoutException:
        print("Timed out waiting for page to load")
        stop_program()

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
            print("Date changed to",DATE)

        except TimeoutException:
            print("Timed out waiting for page to load")
            stop_program()

    showTime = browser.find_element_by_xpath("//*[@id='showEvents']//a/text()[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'%s')]//ancestor::div[@class='listing-info']/div[@class='eventInfo'][contains(text(),'%s')]//ancestor::li[@class='list']/div[2]//div[contains(text(),'%s')]/ancestor::a"%(MOVIE,TYPE,SHOWTIME))
    if 'data-disabled' in showTime.get_attribute("class"):
        print("Sorry! This showtime is either sold out or not available at the moment!")
        stop_program()

    print('Showtime: ', showTime.text, 'selected!')
    time.sleep(random.choice(SMALL_SLEEPS_LIST))
    browser.execute_script("arguments[0].click();", showTime)

    # TODO: For some theatres, terms and conditions is not shown and directly number of seats are chosen, handle that case
    acceptButton = browser.find_element_by_xpath("//*[@id='btnPopupAccept']")
    time.sleep(random.choice(SMALL_SLEEPS_LIST))
    browser.execute_script("arguments[0].click();", acceptButton)
    print("Accepted the terms!")
    # TODO: block multiple seats
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='pop_1']")))
        singleSeat = browser.find_element_by_xpath("//*[@id='pop_1']")
        time.sleep(random.choice(SMALL_SLEEPS_LIST))
        singleSeat.click()
        print("Number of seats: - 1")
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
    except NoSuchElementException:
        print("Unable to locate the number of seat option")
        stop_program()

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

        elif "blocked" in availability:
            print("Sorry! This seat is already booked! Try another.")
            stop_program()

    except TimeoutException:
        print("Timed out waiting for page to load - Seat Chart")
        stop_program()

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
    time.sleep(random.choice(SMALL_SLEEPS_LIST))