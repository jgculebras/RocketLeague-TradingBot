import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException

# SELENIUM OPTIONS
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
chrome_options.add_argument('--start-maximized')

# ROCKET LEAGUE ITEMS COLORS
colors = {"Default": 0,
          "Black": 1,
          "Titanium White": 2,
          "Grey": 3,
          "Crimson": 4,
          "Pink": 5,
          "Cobalt": 6,
          "Sky Blue": 7,
          "Burnt Sienna": 8,
          "Saffron": 9,
          "Lime": 10,
          "Forest Green": 11,
          "Orange": 12,
          "Purple": 13,
          "Gold": 14}

# Prices Dictionary: Key -> Name, Value -> Array of Prices [DEFAULT, BLACK, TW, GREY, CRIMSON, PINK, COBALT, SKY BLUE, BS, SAFFRON, LIME, FG, ORANGE, PURPLE, GOLD]
rlPrices = {"Credits": [1]}

# All Trades Dict
all_trades = []

usernames = []

itemType = ["Decal", "Explosion", "Car", "Wheel", "Boost", "Topper", "Antenna", "Trail", "Banner", "Border", "Engine",
            "Paint"]

discordChannels = {
    "limited": 1130137592873111593,
    "uncommon": 1130137761584787546,
    "rare": 1130137750067216485,
    "very rare": 1130137722372227123,
    "import": 1130137574317498438,
    "exotic": 1130137708765921370,
    "blackmarket": 1130137676171980831
}


# FROM RLINSIDER.gg
def getRLPrices():
    try:
        driver = webdriver.Chrome(options=chrome_options)

        # WAIT TO LOAD DRIVER
        time.sleep(1)

        driver.get("https://rl.insider.gg/en/pc")

        time.sleep(5)

        # FIND CAPTCHA BUTTON
        button = driver.find_element(By.XPATH, '//button[@class="fc-button fc-cta-consent fc-primary-button"]')

        # CLICK CAPTCHA
        button.click()

        time.sleep(5)

        # GET WEBSITE HEIGHT
        current_height = driver.execute_script("return document.body.scrollHeight")

        # SCROLL HEIGHT
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")

            # CHECK IF HEIGHT IS MAX
            if new_height == current_height:
                break

            current_height = new_height

        tr_elements = driver.find_elements(By.CSS_SELECTOR, 'tr[data-iid]')

        # FIND ALL ROWS FOR ITEMS
        for tr in tr_elements:
            # Find the name from the itemNameSpan
            name = tr.find_element(By.CLASS_NAME, 'itemNameSpan').text

            parentdiv = tr.find_element(By.XPATH, "./ancestor::div[contains(@class, 'priceTableContainer')]")

            h2tag = parentdiv.find_element(By.TAG_NAME, 'h2')

            for keyword in itemType:
                if keyword.lower() in h2tag.text.lower():
                    name += " " + keyword.lower()
                    break

            # Find all the <td> elements
            td_elements = tr.find_elements(By.TAG_NAME, 'td')

            td_elements.pop(0)

            # Extract the prices from each <td>
            prices = []
            for td in td_elements:
                if td.get_attribute('class') == 'noHover':
                    prices.append(None)  # Add None for null price
                else:
                    price_split = td.text.replace('\u200a', '').split("-")
                    if len(price_split) > 1 and "k" in price_split[1]:
                        prices.append(float(price_split[0]) * 1000)
                    else:
                        prices.append(td.text.replace('\u200a', '').split("-")[0])

            # Print the extracted data
            rlPrices[name] = prices

    except Exception as e:
        print("Error:", e)

    finally:
        # Close driver
        if driver:
            driver.quit()


# From Rocketleaguegarage.com
def getRLTrades():
    all_trades = []

    driver = webdriver.Chrome(options=chrome_options)

    # Wait to load driver
    time.sleep(1)

    driver.get(
        "https://rocket-league.com/trading?filterItem=0&filterCertification=0&filterPaint=0&filterSeries=A&filterTradeType=0&filterMinCredits=0&filterMaxCredits=100000&filterPlatform%5B%5D=1&filterSearchType=1&filterItemType=0")

    time.sleep(1)

    trades = driver.find_elements(By.CSS_SELECTOR, 'div.rlg-trade')

    for trade in trades:
        trades_items = {}
        trade_has = []
        trade_wants = []

        platform_div = trade.find_element(By.CSS_SELECTOR, "div.rlg-trade__platformname.--no-kerning")
        epic_id = platform_div.text.split("\n")[1]

        usernames.append(epic_id)

        trade_items_has = trade.find_element(By.CSS_SELECTOR, "div.rlg-trade__itemshas")
        trade_items_wants = trade.find_element(By.CSS_SELECTOR, "div.rlg-trade__itemswants")

        item_has = trade_items_has.find_elements(By.CSS_SELECTOR, "div.rlg-item")
        item_wants = trade_items_wants.find_elements(By.CSS_SELECTOR, "div.rlg-item")
        
        for item in item_has:
            item_to_add = {}
            item_name = item.find_element(By.CSS_SELECTOR, "h2.--new.rlg-item__name")
            item_to_add["name"] = item_name.text
            itemtypetoadd = item.find_element(By.CSS_SELECTOR, "a.rlg-btn-primary")
            gradient = item.find_element(By.CSS_SELECTOR, "div.rlg-item__gradient")
            # Get the class attribute value
            class_value = gradient.get_attribute("class")
            item_to_add["gradient"] = class_value.replace("-", "")
        
            for keyword in itemType:
                if keyword.lower() in itemtypetoadd.get_attribute("href").lower():
                    item_to_add["name"] += " " + keyword.lower()
            try:
                item_color = False
                item_color = item.find_element(By.CSS_SELECTOR, "div.rlg-item__paint")
                item_to_add["color"] = item_color.text
            except NoSuchElementException:
                item_to_add["color"] = "Default"
        
            try:
                item_qty = item.find_element(By.CSS_SELECTOR, "div.rlg-item__quantity")
                item_to_add["qty"] = item_qty.text
                trade_has.append(item_to_add)
            except NoSuchElementException:
                item_to_add["qty"] = "1"
                trade_has.append(item_to_add)

        for item in item_wants:
            item_to_add = {}
            item_name = item.find_element(By.CSS_SELECTOR, "h2.--new.rlg-item__name")
            item_to_add["name"] = item_name.text
            itemtypetoadd = item.find_element(By.CSS_SELECTOR, "a.rlg-btn-primary")
            gradient = item.find_element(By.CSS_SELECTOR, "div.rlg-item__gradient")
            # Get the class attribute value
            class_value = gradient.get_attribute("class")
            item_to_add["gradient"] = class_value.replace("-", "")
        
            for keyword in itemType:
                if keyword.lower() in itemtypetoadd.get_attribute("href").lower():
                    item_to_add["name"] += " " + keyword.lower()
            try:
                item_color = False
                item_color = item.find_element(By.CSS_SELECTOR, "div.rlg-item__paint")
                item_to_add["color"] = item_color.text
            except NoSuchElementException:
                item_to_add["color"] = "Default"
        
            try:
                item_qty = item.find_element(By.CSS_SELECTOR, "div.rlg-item__quantity")
                item_to_add["qty"] = item_qty.text
                trade_wants.append(item_to_add)
            except NoSuchElementException:
                item_to_add["qty"] = "1"
                trade_wants.append(item_to_add)

        trades_items["Has"] = trade_has
        trades_items["Wants"] = trade_wants

        all_trades.append(trades_items)

    driver.quit()


def checkGoodTrades():
    for tradeo in range(0, len(all_trades)):
        for index in range(0, len(all_trades[tradeo]["Has"])):
            string_has = ""
            string_has_value = ""
            string_wants = ""
            string_wants_value = ""
            try:
                if index <= len(all_trades[tradeo]["Wants"]):
                    if all_trades[tradeo]["Has"][index]["name"] in rlPrices and all_trades[tradeo]["Wants"][index][
                        "name"] in rlPrices:
                        if all_trades[tradeo]["Has"][index]["color"] is None or all_trades[tradeo]["Has"][index][
                            "color"] == "Default":
                            string_has = "Item Has: " + str(int(all_trades[tradeo]["Has"][index]["qty"])) + " " + str(
                                all_trades[tradeo]["Has"][index]["name"])

                            string_has_value = int(all_trades[tradeo]["Has"][index]["qty"]) * int(
                                rlPrices[all_trades[tradeo]["Has"][index]["name"]][0])
                        else:
                            string_has = "Item Has: " + str(int(all_trades[tradeo]["Has"][index]["qty"])) + " " + str(
                                all_trades[tradeo]["Has"][index]["color"]) + " " + str(
                                all_trades[tradeo]["Has"][index]["name"])

                            string_has_value = int(all_trades[tradeo]["Has"][index]["qty"]) * int(
                                rlPrices[all_trades[tradeo]["Has"][index]["name"]][
                                    colors.get(all_trades[tradeo]["Has"][index]["color"])])
                        if all_trades[tradeo]["Wants"][index]["color"] is None or all_trades[tradeo]["Wants"][index][
                            "color"] == "Default":
                            string_wants = "Item Wants: " + str(
                                int(all_trades[tradeo]["Wants"][index]["qty"])) + " " + str(
                                all_trades[tradeo]["Wants"][index]["name"])

                            string_wants_value = int(all_trades[tradeo]["Wants"][index]["qty"]) * int(
                                rlPrices[all_trades[tradeo]["Wants"][index]["name"]][0])
                        else:
                            string_wants = "Item Wants: " + str(
                                int(all_trades[tradeo]["Wants"][index]["qty"])) + " " + str(
                                all_trades[tradeo]["Wants"][index]["color"]) + " " + str(
                                all_trades[tradeo]["Wants"][index]["name"])

                            string_wants_value = int(all_trades[tradeo]["Wants"][index]["qty"]) * int(
                                rlPrices[all_trades[tradeo]["Wants"][index]["name"]][
                                    colors.get(all_trades[tradeo]["Wants"][index]["color"])])

                        if string_has_value > string_wants_value * 1.5 and "limited" not in \
                                all_trades[tradeo]["Has"][index]["gradient"]:
                            print(usernames[tradeo])
                            print("Item Has:", str(string_has))
                            print("Value:", str(string_has_value))
                            print("Item Wants:", str(string_wants))
                            print("Value:", str(string_wants_value))
                            print()

            except IndexError:
                pass
            except TypeError:
                pass
            except ValueError:
                pass


def main():
    getRLPrices()
    for i in range(0, 100):
        getRLTrades()
        checkGoodTrades()


if __name__ == "__main__":
    main()
