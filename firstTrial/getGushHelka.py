# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd
import numpy as np
url = "https://www.gov.il/apps/mapi/parcel_address/parcel_address.html"

# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL errors


service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)


def get_x_y(addr, city):
    # Wait until the input with id 'addr' is shown
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'addr'))
        )
        print("Element 'addr' is visible")
        element.clear()
        element.send_keys(f"{addr} {city}")
        element.send_keys(Keys.ENTER)
        # Wait until the input with id 'addr' is shown
        try:
            element = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'parcel_ul'))
            )
            content = element.text
            print(content)

            if 'אין תוצאות' in content:
                return str((0, 0))
        except Exception as e:
            print(f"An error occurred: {e}")
            driver.quit()

        time.sleep(2)
        for request in reversed(driver.requests):
            if request.response and request.url == "https://ags.govmap.gov.il/Api/Controllers/GovmapApi/SelectionParams":
                response_body = request.response.body.decode('utf-8')
                response_body = json.loads(response_body)

                geo = response_body['data']['SelectedExtent']
                x = geo['xmin']
                y = geo['ymin']
                print(f"{addr} - {str((x, y))}")
                return str((x, y))
    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()

if __name__ == "__main__":
    city = 'ירושלים'
    driver.get(url) 
    try:
        df = pd.read_csv('מבנים.csv', encoding='utf-8')
        df['geo'] = df.apply(lambda row: get_x_y(f"{row['שם רחוב']} {int(row['מספר בית']) if not np.isnan(row['מספר בית']) else ''}", city), axis=1)
        df.to_csv('מבנים גאו.csv', encoding='utf-8')
    except Exception as e:
        if df is not None:
            df.to_csv('מבנים גאו.csv', encoding='utf-8')
