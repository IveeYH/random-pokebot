from datetime import datetime
import json
import string
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
import random

MAX_OPEN_BATTLES = 2
NAME_CHARACTERS_LIMIT = 15

def is_element(driver: WebDriver, by:str, value: str) -> list[WebElement]:
    try:
        elements = driver.find_elements(by=by, value=value)

        if elements is None:
            return None
        for element in elements:
            if element is not None:
                disabled = element.get_dom_attribute('class')
                if disabled is not None:
                    disabled = 'disabled' in disabled
                else:
                    disabled = False

                choose_disabled = element.get_dom_attribute('name')
                if choose_disabled is not None:
                    choose_disabled = 'chooseDisabled' in choose_disabled
                else:
                    choose_disabled = False

                disabled_att = element.get_dom_attribute('disabled')
                if disabled_att is not None:
                    disabled_att = 'disabled' in disabled_att
                else:
                    disabled_att = False

                print('Actual elements length:',len(elements))

                if (not element.is_displayed()) \
                    or disabled \
                    or choose_disabled \
                    or disabled_att:
                    elements.pop(elements.index(element))
        
        if len(elements) <= 0:
            return None
        return elements
    except common.exceptions.NoSuchElementException:
        return None
    except Exception as e:
        raise e

def click_element(element:WebElement):
    if element.is_displayed():
        element.click()
        return True

    return False

def get_possible_inbattle_options(driver:WebDriver) -> list[WebElement]:
    
    possible_options = is_element(driver, By.NAME, 'chooseMove')

    if possible_options is None:
        possible_options = is_element(driver, By.NAME, 'chooseSwitch')
    else:
        possible_options.extend(is_element(driver, By.NAME, 'chooseSwitch'))

    if possible_options is None:
        return []
    
    i=0
    while i < len(possible_options):
        text = possible_options[i].text
        print(text)

        if text is None:
            possible_options.pop(i)
        else:
            if text.isspace() or text == '':
               possible_options.pop(i)

            i+=1

    return possible_options

def get_battle_navs(driver:WebDriver) -> list[WebElement]:

    drop_overlay = is_element(driver, By.CLASS_NAME, 'ps-overlay')
    if drop_overlay is not None:
        home_drop = is_element(driver, By.CLASS_NAME, 'roomtab')
        if home_drop is not None:
            click_element(home_drop[0])
            sleep(2)

    dropdown = is_element(driver, By.NAME, 'tablist')
    if dropdown is not None:
        click_element(dropdown[0])
        sleep(2)

    drop_overlay = is_element(driver, By.CLASS_NAME, 'ps-overlay')
    if drop_overlay is not None:

        get_list = is_element(driver, By.XPATH, "//div[contains(@class, 'ps-popup')]/li/a[contains(@class, 'roomtab')]")
        if get_list is not None:
            return get_list

    else:
        get_list = is_element(driver, By.CLASS_NAME, 'roomtab')
        if get_list is not None:
            return get_list[1:len(get_list)-1:]


def add_battle(driver:WebDriver, online_battles:dict):

    print('Searching battles...')

    search_counter = 0

    all_tabs = get_battle_navs(driver)
    if all_tabs is not None:
        search_counter=len(all_tabs)
    
    while search_counter < MAX_OPEN_BATTLES:

        sleep(2)

        home_nav = is_element(driver, By.XPATH, "//div[@class='tabbar maintabbar']/div/ul[1]/li[1]/a[@href='/']")
        if home_nav is not None:
            click_element(home_nav[0])
            sleep(2)

        show_search = is_element(driver, By.XPATH, "//button[@name='showSearchGroup']")

        if show_search is not None:
            click_element(show_search[0])
            sleep(2)

        search = is_element(driver, By.XPATH, "//button[@name='search']")
        if search is not None:
            click_element(search[0])
            sleep(2)

            search_counter+=1

        

        while len(online_battles.keys())+1 != len(all_tabs):

            sleep(1)

            all_tabs = get_battle_navs(driver)

            #print('Ya sale a ver\n', all_tabs)

        battle_ref = all_tabs[len(online_battles.keys())].get_property("href")
        online_battles[battle_ref] = {'start_battle':datetime.now().strftime('%Y%m%dT%H%M%S')}

        while True:
            sleep(1)

            options = get_possible_inbattle_options(driver)

            print('Options length:',len(options))

            if len(options) > 0:

                timer_button = is_element(driver, By.NAME, 'openTimer')

                print('Timer button length:',len(timer_button))

                if timer_button is not None:
                    
                    if 'Timer' not in timer_button[-1].text:
                        break

                    click_element(timer_button[-1])
                    sleep(0.5)

                    timer_on = is_element(driver, By.NAME, 'timerOn')
                    if timer_on is not None:
                        click_element(timer_on[0])
                        sleep(2)
                        break

        print('Added battle number:', search_counter)

def main():

    

    browser_options = webdriver.ChromeOptions()
    browser_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_driver_binary = "chrome-driver/chromedriver"
    chrome_driver = webdriver.Chrome(chrome_driver_binary, options=browser_options)

    chrome_driver.get('https://play.pokemonshowdown.com/')

    # chrome_driver.maximize_window()

    if not "Showdown!" in chrome_driver.title:
        raise Exception('Pokemon Showdown is not working.')

    sleep(2)


    # REJECT COOKIES

    deny_cookies = is_element(chrome_driver, By.XPATH, "//div[@class='qc-cmp2-summary-buttons']/button[1]")
    if deny_cookies is not None:
        click_element(deny_cookies[0])
        sleep(2)

    print('Cookies rejected...')


    # LOGIN PROCESS

    login = is_element(chrome_driver, By.XPATH, "//button[@name='login']")

    if login is not None:

        click_element(login[0])

        sleep(2)
        
        user_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=NAME_CHARACTERS_LIMIT))

        log_user = is_element(chrome_driver, By.XPATH, "//input[@name='username']")
        
        if log_user is not None:

            log_user[0].send_keys(user_name + Keys.ENTER)
            sleep(2)
    
    print('Log in successful...')

    # CHECK PRIVATE FIGHTS
    private_checkbox = is_element(chrome_driver, By.XPATH,"//input[@name='private']")

    if not private_checkbox[0].is_selected():
        click_element(private_checkbox[0])

        sleep(1)

    # SEARCH BATTLE IN HOME
    online_battles = {}

    add_battle(chrome_driver, online_battles)

    print('Comenzando a combatir...')

    battle_id = 0
    rounds = 0
    while True:

        sleep(1)

        battle_keys = list(online_battles.keys())
        current_battle_key = battle_keys[battle_id]
        battle_key = current_battle_key[32::]

        dropdown = is_element(chrome_driver, By.NAME, 'tablist')
        if dropdown is not None:
            click_element(dropdown[0])
            sleep(2)

            tabs = is_element(chrome_driver, By.XPATH, f"//a[@href='{battle_key}']")
            if tabs is not None:
                click_element(tabs[len(tabs)-1])
                sleep(2)

        else:
            tabs = is_element(chrome_driver, By.XPATH, f"//a[@href='{battle_key}']")
            if tabs is not None:
                click_element(tabs[0])
                sleep(2)

        # PICK RANDOM OPTION BATTLE 
        is_move_menu_available = False
        
        while not is_move_menu_available:

            sleep(1)

            close_battle = is_element(chrome_driver, By.XPATH, "//button[@name='closeAndMainMenu']")
            if close_battle is not None:
                click_element(close_battle[0])
                sleep(2)

                finalized_battle = online_battles.pop(current_battle_key)

                with open('./battle-tests/'+finalized_battle['start_battle']+'.json', 'w') as file:
                    json.dump({current_battle_key:finalized_battle}, file, indent=1)

                add_battle(chrome_driver, online_battles)
            
            else:
                options = get_possible_inbattle_options(chrome_driver)

                len_options = len(options)

                if len_options > 0:
                    selected_option = random.randint(0, len_options-1)

                    print('Final option:', options[selected_option].tag_name,options[selected_option].get_dom_attribute('name'),options[selected_option].text,options[selected_option].is_displayed())

                    click_element(options[selected_option])
                    sleep(2)

                    is_move_menu_available = True
            

        if battle_id < len(battle_keys)-1:
            battle_id += 1
        else:
            battle_id = 0
            rounds += 1
            print('Round', rounds)

        if rounds > 100:
            break

    chrome_driver.quit()


if __name__ == '__main__':
    main()