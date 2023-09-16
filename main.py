import os

from selenium.common import StaleElementReferenceException

from selenium.webdriver.support import expected_conditions as EC
from time import sleep

from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import mysql.connector
import sys

from datetime import datetime, date

from Configuration_Page import *


# for instantiate Chrome web driver
def configuration():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    browser = webdriver.Chrome()
    browser.maximize_window()
    return browser  #


##########################################


# scrape seaworld orlando  , prices and make calculations
def scrape_seaworld_prices(browser):
    browser.get('https://seaworld.com/orlando/tickets/')
    calendar_form = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.form__datepicker'
                                                                                                  '-wrapper'
                                                                                                  '.spinner__parent')))
    calendar_form.click()
    sleep(40)  # 20

    # close_btn = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "bx-close-inside-2052025")))
    try:
        close_btn = browser.find_element(By.ID, "bx-close-inside-2052025")
        close_btn.click()
    except:
        pass
    sleep(5)
    date_pick = browser.find_element(By.CSS_SELECTOR, ".selectric-wrapper.selectric-dynamic-calendar-modal__months"
                                                      ".selectric-js-selectric")

    prices = []
    dates = []
    months = browser.find_elements(By.CSS_SELECTOR, ".calendar-modal__months-wrapper ul li")
    for month in months:
        indx = months.index(month) + 1
        scrape_month_daily_prices(browser, date_pick, month, prices, dates, indx)
    PARK_PRICES = [
        int(
            round(
                (float(price.replace('$', '')) + (float(price.replace('$', '')) * 0.065))
                , 0
            )
        )
        for price in
        prices]
    OUR_PRICES = [
        int(
            round(
                (float(price.replace('$', '')) - (float(price.replace('$', '')) * SeaWorld_Orlando_DISCOUNT)) / 5,
                0)  # 0.3 is discount for seaworld
            * 5)
        for price in
        prices]
    for my_date in dates:
        x = my_date.split('/')
        date_r = '-'.join([x[2], x[0], x[1]])
        if date(int(x[2]), int(x[0]), int(x[1])) >= date.today():
            Seaworld_DATES.append(date_r)
    for price in PARK_PRICES:
        Seaworld_PARK_PRICE.append(str(price))
    for price in OUR_PRICES:
        Seaworld_OUR_PRICE.append(str(price))


# this functions is called by the above funtion is used to scrape the dates and the prices for each month then those
# scraped information are used by the above funtion to make the calculations
def scrape_month_daily_prices(browser, date_pick, month, prices, dates, indx):
    try:
        date_pick.click()

    except StaleElementReferenceException as e:
        date_pick = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".selectric-wrapper.selectric-dynamic-calendar-modal__months"
                                  ".selectric-js-selectric")))
        date_pick.click()
    sleep(2)

    try:
        month.click()

    except StaleElementReferenceException as e:
        month = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".calendar-modal__months-wrapper ul li:nth-child({})".format(indx))))
        month.click()
    sleep(3)
    days = browser.find_elements(By.CSS_SELECTOR,
                                 ".dynamic-calendar-modal__container tr td ul li:nth-child(1)")

    dates_boxes = browser.find_elements(By.CSS_SELECTOR,
                                        ".dynamic-calendar-modal__day")
    null_dates_boxes = browser.find_elements(By.CSS_SELECTOR, ".calendar-modal__day--is-null")

    for day in days:
        price = day.find_elements(By.CSS_SELECTOR, "span span")
        prices.append("".join([part.text for part in price]))
    # print(prices)
    sleep(3)

    for my_date in dates_boxes:
        if my_date not in null_dates_boxes:
            dates.append(my_date.get_attribute("data-date"))  # + " Seaworld admission")
            # final_results_seawrold["date"].append(date.get_attribute("data-date"))


############################################################################

# this function is used to scrape both universal orlando one park and park to park and it makes the calculations
def scrape_universal_orlando(browser):
    from datetime import date
    result_two_park = []
    result_one_park = []

    browser.get("https://www.universalorlando.com/web-store/en/us/park-tickets?flr=0&days=1")
    sleep(5)  # 5
    increase_btn = browser.find_element(By.CSS_SELECTOR, ".guest-number-increase-button")
    increase_btn.click()
    sleep(5)
    select_date_btn = browser.find_element(By.CSS_SELECTOR, ".purchase-card-btn-select")
    select_date_btn.click()
    sleep(5)
    # WebDriverWait(browser, 200).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.gds-calendar-controls')))

    j = 0
    while j < 3:
        dates_boxes_1 = browser.find_elements(By.CSS_SELECTOR, "gds-calendar-day.hydrated")
        prices_boxes = browser.find_elements(By.CSS_SELECTOR, ".gds-eyebrow.label-13.theme-default")
        dates = []
        for my_date in dates_boxes_1:
            if len(str(my_date.get_attribute("data-date"))) >= 10:
                x = my_date.get_attribute("data-date").split('-')
                if date(int(x[2]), int(x[0]), int(x[1])) >= date.today():
                    date_r = '-'.join([x[2], x[0], x[1]])
                    dates.append(date_r)
            else:
                # dates.append(date.get_attribute("data-date"))
                """x = my_date.get_attribute("data-date").split('-')
                if date(int(x[2]), int(x[0]), int(x[1])) >= date.today():
                    date_r = '-'.join([x[2], x[0], x[1]])
                    dates.append(date_r)"""

        prices = [price.text for price in prices_boxes]
        for i in zip(dates, prices):
            row = " ".join(i)
            if row not in result_two_park:
                result_two_park.append(row)
        sleep(30)

        btn = browser.find_elements(By.CSS_SELECTOR, ".right-arrow")[4]
        browser.execute_script("arguments[0].click()", btn)
        sleep(5)  # 10
        j += 1
    DATES = [row.split(" ")[0] for row in result_two_park]
    PARK_PRICE = [
        int(
            round(
                float(row.split(" ")[1].replace('$', '')) + float(row.split(" ")[1].replace('$', '')) * 0.065, 0
            )
        )
        for row in result_two_park]
    OUR_PRICE = [
        int(
            round(
                (float(row.split(" ")[1].replace('$', '')) + (
                        float(row.split(" ")[1].replace('$', '')) * 0.065) - Universal_Orlando_PTP_DISCOUNT) / 5,
                0) * 5)
        for row in result_two_park]
    for my_date in DATES:
        Universal_two_park_DATES.append(my_date)
    for park_price in PARK_PRICE:
        Universal_two_park_PARK_PRICE.append(str(park_price))
    for our_price in OUR_PRICE:
        Universal_two_park_OUR_PRICE.append(str(our_price))

    # print('########################################################################################')
    browser.get("https://www.universalorlando.com/web-store/en/us/park-tickets?flr=0&days=1")
    sleep(5)
    browser.find_elements(By.CSS_SELECTOR, ".guest-number-increase-button")[2].click()
    sleep(5)
    browser.find_elements(By.CSS_SELECTOR, ".purchase-card-btn-select")[1].click()
    sleep(5)
    # WebDriverWait(browser, 200).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.gds-calendar-controls')))
    j = 0
    while j < 3:
        dates_boxes_1 = browser.find_elements(By.CSS_SELECTOR, "gds-calendar-day.hydrated")
        prices_boxes = browser.find_elements(By.CSS_SELECTOR, ".gds-eyebrow.label-13.theme-default")
        dates = []
        for my_date in dates_boxes_1:
            if len(str(my_date.get_attribute("data-date"))) < 10:
                continue
            else:
                # dates.append(date.get_attribute("data-date"))
                x = my_date.get_attribute("data-date").split('-')
                if date(int(x[2]), int(x[0]), int(x[1])) >= date.today():
                    date_r = '-'.join([x[2], x[0], x[1]])
                    dates.append(date_r)

        prices = [price.text for price in prices_boxes]

        for i in zip(dates, prices):
            row = " ".join(i)
            if row not in result_one_park:
                result_one_park.append(row)
        sleep(30)
        btn = browser.find_elements(By.CSS_SELECTOR, ".right-arrow")[4]
        browser.execute_script("arguments[0].click()", btn)
        sleep(5)  # 10
        j += 1
    DATES = [row.split(" ")[0] for row in result_one_park]
    PARK_PRICE = [
        int(round(float(row.split(" ")[1].replace('$', '')) + float(row.split(" ")[1].replace('$', '')) * 0.065, 0))
        for row in result_one_park]
    OUR_PRICE = [
        int(round(
            (float(row.split(" ")[1].replace('$', '')) + (
                    float(row.split(" ")[1].replace('$', '')) * 0.065) - Universal_Orlando_ONEPARK_DISCOUNT) / 5,
            0) * 5)
        for row in result_one_park]
    for my_date in DATES:
        Universal_one_park_DATES.append(my_date)
    for park_price in PARK_PRICE:
        Universal_one_park_PARK_PRICE.append(str(park_price))
    for our_price in OUR_PRICE:
        Universal_one_park_OUR_PRICE.append(str(our_price))


################################################################################

# this function is used to scrape two park express and it makes the calculations
def two_park_express(browser):
    result_two_park_express = []
    browser.get("https://www.universalorlando.com/web-store/en/us/uotickets/express-pass")
    sleep(5)  # 5
    browser.find_elements(By.CSS_SELECTOR, ".guest-number-increase-button")[0].click()
    sleep(5)
    browser.find_elements(By.CSS_SELECTOR, ".purchase-card-btn-select")[0].click()
    sleep(5)
    while 1:
        days = browser.find_elements(By.ID, "dayButton")

        prices = browser.find_elements(By.CSS_SELECTOR, ".calendar-price span")

        j = 0  # for prices
        k = 1  # counter for the days indexes start from 1 to 31
        for day in days:
            #
            parts = day.get_attribute("link-title").split(" ")
            if int(parts[14]) == k:
                """if k == 31 and int(parts[14]) == 1:
                    break"""
                if "inactive-day" in day.get_attribute("class").split(" "):
                    k += 1
                    j = 0
                    continue
                row = "-".join([parts[12], MONTHS[parts[11]], parts[14]]) + " " + str(
                    prices[j].text)
                # j += 1
                k += 1

                result_two_park_express.append(row)
            j += 1
        try:
            browser.find_element(By.CSS_SELECTOR, ".icon.icon-arrow-right").click()
            sleep(5)
        except common.exceptions.ElementNotInteractableException:
            DATES = [row.split(" ")[0] for row in result_two_park_express]
            PARK_PRICE = [
                int(round(float(row.split(" ")[1].replace('$', '')) + float(row.split(" ")[1].replace('$', '')) * 0.065,
                          0))
                for row in result_two_park_express]

            OUR_PRICE = [
                int(
                    round(
                        (float(row.split(" ")[1].replace('$', '')) - (
                                float(row.split(" ")[1].replace('$', '')) * TWO_PARK_EXPRESS_DISCOUNT))
                        / 5
                        , 0)
                    * 5)
                for row in result_two_park_express]

            for date in DATES:
                Universal_two_park_EXPRESS_DATES.append(date)
            for park_price in PARK_PRICE:
                Universal_two_park_EXPRESS_PARK_PRICES.append(str(park_price))
            for our_price in OUR_PRICE:
                Universal_two_park_EXPRESS_OUR_PRICES.append(str(our_price))

            return


#################################################################################

# this function is used to scrape one park express and it makes the calculations
def one_park_express(browser):
    result_one_park_express = []
    browser.get("https://www.universalorlando.com/web-store/en/us/uotickets/express-pass")
    sleep(5)  # was 20
    browser.find_element(By.ID, "dayIndex1").click()
    sleep(5)
    browser.find_elements(By.CSS_SELECTOR, ".guest-number-increase-button")[2].click()
    sleep(5)
    browser.find_elements(By.CSS_SELECTOR, ".purchase-card-btn-select")[2].click()
    sleep(5)
    while 1:
        days = browser.find_elements(By.ID, "dayButton")

        prices = browser.find_elements(By.CSS_SELECTOR, ".calendar-price span")

        j = 0  # for prices
        k = 1  # counter for the days indexes start from 1 to 31
        for day in days:
            #
            parts = day.get_attribute("link-title").split(" ")
            if int(parts[19]) == k:
                """if k == 31 and int(parts[14]) == 1:
                    break"""
                if "inactive-day" in day.get_attribute("class").split(" "):
                    k += 1
                    j = 0
                    continue
                row = "-".join([parts[17], MONTHS[parts[16]], parts[19]]) + " " + str(
                    prices[j].text)
                # j += 1
                k += 1

                result_one_park_express.append(row)
            j += 1
        try:
            browser.find_element(By.CSS_SELECTOR, ".icon.icon-arrow-right").click()
            sleep(5)  # 5
        except common.exceptions.ElementNotInteractableException:
            DATES = [row.split(" ")[0] for row in result_one_park_express]
            PARK_PRICE = [
                int(round(float(row.split(" ")[1].replace('$', '')) + float(row.split(" ")[1].replace('$', '')) * 0.065,
                          0))
                for row in result_one_park_express]

            OUR_PRICE = [
                int(
                    round(
                        (float(row.split(" ")[1].replace('$', '')) - (
                                float(row.split(" ")[1].replace('$', '')) * ONE_PARK_EXPRESS_DISCOUNT))
                        / 5, 0) * 5
                )
                for row in result_one_park_express]

            for date in DATES:
                Universal_one_park_EXPRESS_DATES.append(date)
            for park_price in PARK_PRICE:
                Universal_one_park_EXPRESS_PARK_PRICES.append(str(park_price))
            for our_price in OUR_PRICE:
                Universal_one_park_EXPRESS_OUR_PRICES.append(str(our_price))

            return


##################################################################################

# this function is used to scrape both HHN express and HHN admission, and it makes the calculations
def HHN(browser, express):
    result_hhn = []
    browser.get("https://www.universalorlando.com/web-store/en/us/uotickets/add-ons")
    sleep(5)  # 20
    """hhn_tab = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-tabs li:nth-child(2)")))"""
    hhn_tab = browser.find_element(By.CSS_SELECTOR, ".product-tabs li:nth-child(2)")
    hhn_tab.click()
    sleep(5)  # 10
    if express:
        browser.find_elements(By.CSS_SELECTOR, ".button-primary")[1].click()
        product = " Universal HHN express  "
    else:
        browser.find_elements(By.CSS_SELECTOR, ".button-primary")[0].click()
        product = " Universal HHN admission  "

    ###############################################
    increase_btn = WebDriverWait(browser, 50).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".guest-number-increase-button")))
    increase_btn.click()

    #################################################
    next_btn = WebDriverWait(browser, 50).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".primary.theme-default")))
    next_btn.click()
    sleep(5)  # 10
    ###################################################
    while 1:
        days = browser.find_elements(By.ID, "dayButton")

        prices = browser.find_elements(By.CSS_SELECTOR, ".calendar-price span")
        available_prices = []
        for price in prices:
            if price.get_attribute("class") != "sold-out-day":
                available_prices.append(price)

        j = 0  # for prices
        k = 1  # counter for the days indexes start from 1 to 31
        for day in days:
            #
            parts = day.get_attribute("link-title").split(" ")
            if int(parts[15]) == k:
                """if k == 31 and int(parts[14]) == 1:
                    break"""
                if "inactive-day" in day.get_attribute("class").split(" "):
                    k += 1
                    continue
                row = "-".join([parts[13], MONTHS[parts[12]], parts[15]]) + " " + str(
                    available_prices[j].text)
                j += 1
                k += 1
                result_hhn.append(row)
            elif "inactive-day" not in day.get_attribute("class").split(" "):
                j += 1
        try:
            browser.find_element(By.CSS_SELECTOR, ".icon.icon-arrow-right").click()
            sleep(5)  # 10
        except:
            # return result_hhn
            DATES = [row.split(" ")[0] for row in result_hhn]
            PARK_PRICE = [
                int(
                    round(
                        float(row.split(" ")[1].replace('$', '')) + float(row.split(" ")[1].replace('$', '')) * 0.065,
                        0)
                )
                for row in result_hhn]
            if express == False:
                OUR_PRICE = [
                    int(round((float(row.split(" ")[1].replace('$', '')) + (
                            float(row.split(" ")[1].replace('$', '')) * 0.065) - HHN_ADMISSION_DISCOUNT) / 5, 0) * 5)
                    for row in result_hhn]
            else:
                OUR_PRICE = [
                    int(round((float(row.split(" ")[1].replace('$', '')) - (
                            float(row.split(" ")[1].replace('$', '')) * HHN_EXPRESS_DISCOUNT)) / 5, 0) * 5)
                    for row in result_hhn]
            if express == False:
                for my_date in DATES:
                    HHN_DATES.append(my_date)
                for park_price in PARK_PRICE:
                    HHN_PARK_PRICES.append(str(park_price))
                for our_price in OUR_PRICE:
                    HHN_OUR_PRICES.append(str(our_price))

            else:
                for my_date in DATES:
                    HHN_EXPRESS_DATES.append(my_date)
                for park_price in PARK_PRICE:
                    HHN_EXPRESS_PARK_PRICES.append(str(park_price))
                for our_price in OUR_PRICE:
                    HHN_EXPRESS_OUR_PRICES.append(str(our_price))

            return


###################################################################################

# this funtion is used to update the database , you have to set the database host, username , password ,
# port and database name from Configuration page
def update_database():  # function to update database
    try:
        cnx = mysql.connector.connect(
            host=database_host,  # database host
            database=database_name,  # database name
            user=database_username,  # database username
            password=database_password,  # database password
            port=database_port  # database port
        )
        if cnx.is_connected():
            select_ids = """
                              SELECT id FROM ticket_prices WHERE ticket_id = %s
                         """
            update_query = """ 
                              update ticket_prices SET date=%s, park_price=%s,price=%s WHERE id = %s;
                           """

            ids_list = []
            ids_record = []
            cursor = cnx.cursor()
            ###########################
            seaworld_admission = []
            universal_one_park = []
            universal_park_to_park = []
            hhn_admission = []
            hhn_express = []
            universal_one_park_express = []
            universal_two_park_express = []
            ##########################

            products = {
                "1": [37],
                "2": [2, 44, 83, 84, 85, 86],
                "3": [52, 55, 102, 103, 100, 101],
                "4": [39],
                "5": [40, 95],
                "6": [104, 106],
                "7": [105, 107]
            }
            for product_ids in products.keys():
                for ticket_id in products[product_ids]:
                    cursor.execute(select_ids, (ticket_id,))
                    records = cursor.fetchall()
                    for record in records:
                        for id_ in record:
                            ids_record.append(id_)

                    ids_list.append(ids_record)
                    ids_record = []

            j = 0
            for i in range(len(products["1"])):
                seaworld_admission.append([(i[0], int(i[1]), int(i[2]), i[3]) for i in
                                           zip(Seaworld_DATES[:90], Seaworld_PARK_PRICE[:90], Seaworld_OUR_PRICE[:90],
                                               ids_list[j])])
                j += 1

            for i in range(len(products["2"])):
                universal_one_park.append([(i[0], i[1], i[2], i[3]) for i in
                                           zip(Universal_one_park_DATES[:90], Universal_one_park_PARK_PRICE[:90],
                                               Universal_one_park_OUR_PRICE[:90],
                                               ids_list[j])
                                           ])
                j += 1

            for i in range(len(products["3"])):
                universal_park_to_park.append([(i[0], i[1], i[2], i[3]) for i in
                                               zip(Universal_two_park_DATES[:90], Universal_two_park_PARK_PRICE[:90],
                                                   Universal_two_park_OUR_PRICE[:90],
                                                   ids_list[j])])
                j += 1

            for i in range(len(products["4"])):
                hhn_admission.append([(i[0], i[1], i[2], i[3]) for i in
                                      zip(HHN_DATES[:60], HHN_PARK_PRICES[:60], HHN_OUR_PRICES[:60], ids_list[j])])
                j += 1

            for i in range(len(products["5"])):
                hhn_express.append([(i[0], i[1], i[2], i[3]) for i in
                                    zip(HHN_EXPRESS_DATES[:60], HHN_EXPRESS_PARK_PRICES[:60],
                                        HHN_EXPRESS_OUR_PRICES[:60],
                                        ids_list[j])])
                j += 1

            for i in range(len(products["6"])):
                universal_one_park_express.append([(i[0], i[1], i[2], i[3]) for i in
                                                   zip(Universal_one_park_EXPRESS_DATES[:90],
                                                       Universal_one_park_EXPRESS_PARK_PRICES[:90],
                                                       Universal_one_park_EXPRESS_OUR_PRICES[:90], ids_list[j])])
                j += 1

            for i in range(len(products["7"])):
                universal_two_park_express.append([(i[0], i[1], i[2], i[3]) for i in
                                                   zip(Universal_two_park_EXPRESS_DATES[:90],
                                                       Universal_two_park_EXPRESS_PARK_PRICES[:90],
                                                       Universal_two_park_EXPRESS_OUR_PRICES[:90], ids_list[j])])
                j += 1

            tickets = [
                seaworld_admission,
                universal_one_park,
                universal_park_to_park,
                hhn_admission,
                hhn_express,
                universal_one_park_express,
                universal_two_park_express
            ]
            for ticket in tickets:
                for ids in ticket:
                    cursor.executemany(update_query, ids)

            cnx.commit()
            cursor.close()
        cnx.close()
    except:
        print('error')


#####################################################################################
if __name__ == '__main__':
    MONTHS = {
        "January": '1',
        "February": '2',
        "March": '3',
        "April": '4',
        "May": '5',
        'June': '6',
        'July': '7',
        'August': '8',
        'September': '9',
        'October': '10',
        'November': '11',
        'December': '12',
    }
    # seaworld orlando
    Seaworld_DATES = ["dates"]  # dates
    Seaworld_PARK_PRICE = ["park price"]  # park prices
    Seaworld_OUR_PRICE = ["our price"]  # our price

    # universal one park
    Universal_one_park_DATES = ['dates']  # dates
    Universal_one_park_PARK_PRICE = ['park price']  # park prices
    Universal_one_park_OUR_PRICE = ['our price']  # our price

    # universal park to park
    Universal_two_park_DATES = []  # dates
    Universal_two_park_PARK_PRICE = []  # park price
    Universal_two_park_OUR_PRICE = []  # our price

    # HHN admission
    HHN_DATES = []  # dates
    HHN_PARK_PRICES = []  # park price
    HHN_OUR_PRICES = []  # our price

    # HHN EXPRESS
    HHN_EXPRESS_DATES = []  # dates
    HHN_EXPRESS_PARK_PRICES = []  # park price
    HHN_EXPRESS_OUR_PRICES = []  # our price

    # Universal one park express
    Universal_one_park_EXPRESS_DATES = []  # dates
    Universal_one_park_EXPRESS_PARK_PRICES = []  # park price
    Universal_one_park_EXPRESS_OUR_PRICES = []  # our price

    # Universal one park express
    Universal_two_park_EXPRESS_DATES = []  # dates
    Universal_two_park_EXPRESS_PARK_PRICES = []  # park price
    Universal_two_park_EXPRESS_OUR_PRICES = []  # our price

    driver = configuration()
    scrape_seaworld_prices(driver)  # for seaworld admission
    sleep(5)
    scrape_universal_orlando(driver)  # for both universal orlando one park and park to park
    sleep(5)
    HHN(driver, False)  # for HHN admission
    sleep(5)
    HHN(driver, True)  # for HHN express
    sleep(5)
    one_park_express(driver)  # for universal orlando one park express
    sleep(5)
    two_park_express(driver)  # for universal orlando two park express"""
    sleep(5)
    driver.close()

    print("seaworld orlando admission ")
    data = [(i[0], i[1], i[2]) for i in
            zip(Seaworld_DATES[:91], Seaworld_PARK_PRICE[:91], Seaworld_OUR_PRICE[:91],
                )]
    for i in data:
        print(i[0] + "     " + str(i[1]) + "       " + str(i[2]))

    print("universal one park ")
    data = [(i[0], i[1], i[2]) for i in
            zip(Universal_one_park_DATES[:91], Universal_one_park_PARK_PRICE[:91],
                Universal_one_park_OUR_PRICE[:91],
                )]
    for i in data:
        print(i[0] + "     " + str(i[1]) + "       " + str(i[2]))

    print("universal park to park ")
    data = [(i[0], i[1], i[2]) for i in
            zip(Universal_two_park_DATES[:91], Universal_two_park_PARK_PRICE[:91],
                Universal_two_park_OUR_PRICE[:91],
                )]
    for i in data:
        print(i[0] + "     " + str(i[1]) + "       " + str(i[2]))

    print("HHN admission ")
    data = [(i[0], i[1], i[2]) for i in
            zip(HHN_DATES, HHN_PARK_PRICES, HHN_OUR_PRICES,
                )]
    for i in data:
        print(i[0] + "     " + str(i[1]) + "       " + str(i[2]))

    print("HHN express ")
    data = [(i[0], i[1], i[2]) for i in
            zip(HHN_EXPRESS_DATES, HHN_EXPRESS_PARK_PRICES, HHN_EXPRESS_OUR_PRICES,
                )]
    for i in data:
        print(i[0] + "     " + str(i[1]) + "       " + str(i[2]))

    print("universal one park express")
    data = [(i[0], i[1], i[2]) for i in
            zip(Universal_one_park_EXPRESS_DATES[:91], Universal_one_park_EXPRESS_PARK_PRICES[:91],
                Universal_one_park_EXPRESS_OUR_PRICES[:91],
                )]
    for i in data:
        print(i[0] + "     " + str(i[1]) + "       " + str(i[2]))

    print("universal two park express")
    data = [(i[0], i[1], i[2]) for i in
            zip(Universal_two_park_EXPRESS_DATES[:91], Universal_two_park_EXPRESS_PARK_PRICES[:91],
                Universal_two_park_EXPRESS_OUR_PRICES[:91],
                )]
    for i in data:
        print(i[0] + "     " + str(i[1]) + "       " + str(i[2]))

    # update_database() # apply updates to the database

# live:.cid.d8714142d936746d
