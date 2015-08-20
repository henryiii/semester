#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, TimeoutException
from selenium.webdriver.support import expected_conditions

blank_path = r"//input[@class='question_input'][@value='--']"
btn_path = r"//button[@type='submit']"
NO_SUB_ID = 'this_student_does_not_have_a_submission'
from selenium.webdriver.common.by import By

def locator(driver):
	return (expected_conditions.presence_of_element_located((By.CLASS_NAME, 'question_input'),)(driver)
		or  expected_conditions.presence_of_element_located((By.ID, NO_SUB_ID),)(driver))

def main():
    driver = webdriver.Firefox()

    driver.get('https://utexas.instructure.com')
    driver.implicitly_wait(10)

    input('Open the page you want to grade, then press enter on this terminal')

    while True:
            try:
                    driver.switch_to.frame('speedgrader_iframe')
            except AttributeError:
                    pass

            while len(driver.find_elements_by_xpath(blank_path)) or len(driver.find_elements_by_id(NO_SUB_ID)) > 0:
                    blanks = driver.find_elements_by_xpath(blank_path)
                    if len(blanks) > 0:
                            for blank in blanks:
                                    try:
                                            blank.click()
                                            blank.send_keys('0')
                                    except ElementNotVisibleException:
                                            pass

                            driver.implicitly_wait(1)
                            btn = driver.find_element_by_xpath(btn_path)
                            driver.implicitly_wait(1)
                            btn.click()

                    driver.switch_to.parent_frame()
                    driver.implicitly_wait(1)
                    driver.find_element_by_class_name('next').click()
                    driver.implicitly_wait(3)
                    driver.switch_to.frame('speedgrader_iframe')
                    try:
                            WebDriverWait(driver,15).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'question_input'),))
                    except TimeoutException:
                            break

            v = input('Next? Enter to continue or Q enter to quit: ')
            if v.lower() in ('q','c','n'):
                    break

if __name__ == '__main__':
    main()
