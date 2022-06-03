from datetime import datetime
import string
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import random

def main():

    browser_options = webdriver.ChromeOptions()
    browser_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_driver_binary = "chrome-driver/chromedriver"
    chrome_driver = webdriver.Chrome(chrome_driver_binary, chrome_options=browser_options)

    chrome_driver.get('https://play.pokemonshowdown.com/')

    chrome_driver.maximize_window()

    if not "Showdown!" in chrome_driver.title:
        raise Exception('Pokemon Showdown is not working.')

    time_now_str = datetime.now().strftime('%Y%m%dT%H%M%S%z')

    run_dict = {
        time_now_str: {
            'successful_login' : False
        }
    }

    sleep(2)

    # REJECT COOKIES
    try:
        chrome_driver.find_element(by=By.XPATH, value="//div[@class='qc-cmp2-summary-buttons']/button[1]").click()
    except common.exceptions.NoSuchElementException:
        print("There's no cookie accept.")
    except Exception as e:
        raise e
    
    sleep(0.5)

    # LOGIN PROCESS
    login_user_need = True

    try:
        chrome_driver.find_element(by=By.NAME, value="login").click()
    except common.exceptions.NoSuchElementException:
        print("There's no login needed.")

        login_user_need = False

    except Exception as e:
        raise e

    sleep(2)

    # SET USERNAME
    NAME_CHARACTERS_LIMIT = 18
    
    user_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=NAME_CHARACTERS_LIMIT))

    if login_user_need:
        chrome_driver.find_element(by=By.NAME, value="username").send_keys(user_name + Keys.ENTER)

    run_dict[time_now_str]['successful_login'] = True

    sleep(2)
    


    # CHECK PRIVATE FIGHTS
    private_checkbox = chrome_driver.find_element(by=By.NAME, value="private")

    if not private_checkbox.is_selected():
        private_checkbox.click()
    
    chrome_driver.find_element(by=By.NAME, value="search").click()

    sleep(10)


    # GO HOME
    chrome_driver.find_element(by=By.XPATH, value="//div[@class='tabbar maintabbar']/div/ul[1]/li[1]/a[@href='/']").click()


    sleep(5)



    # chrome_driver.find_element_by_name("li1").click()

    # chrome_driver.find_element_by_name("li2").click()

    # title = "Sample page - lambdatest.com"

    # assert title == chrome_driver.title

    # sample_text = "Happy Testing at LambdaTest"

    # email_text_field = chrome_driver.find_element_by_id("sampletodotext")

    # email_text_field.send_keys(sample_text)

    # sleep(5)

    # chrome_driver.find_element_by_id("addbutton").click()

    # sleep(5)

    # output_str = chrome_driver.find_element_by_name("li6").text

    # sys.stderr.write(output_str)

    # sleep(2)

    print(run_dict)

    chrome_driver.quit()


if __name__ == '__main__':
    main()