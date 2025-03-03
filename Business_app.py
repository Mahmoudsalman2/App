
import requests
from PIL import Image
from io import BytesIO
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to convert currency using an API
def convert_currency(amount, from_currency, to_currency):
    # API endpoint for currency conversion
    api_endpoint = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    # Get latest exchange rates
    response = requests.get(api_endpoint)
    data = response.json()
    # Convert the amount to the target currency
    converted_amount = amount * data['rates'][to_currency]
    return converted_amount

# Function to get user's country based on IP address
def get_user_country():
    try:
        # Get user's IP address
        ip_response = requests.get('https://api.ipify.org?format=json')
        ip_data = ip_response.json()
        ip_address = ip_data['ip']
        # Get user's country based on IP address
        country_response = requests.get(f'https://ipapi.co/{ip_address}/country/')
        user_country = country_response.text
        return user_country
    except Exception as e:
        print("Error getting user's country:", e)
        return None

# Dictionary mapping country codes to currency codes
country_to_currency = {
    'US': 'USD',
    'GB': 'GBP',
    'EU': 'EUR',  # Add more mappings as needed
    "Eg": "EGP",
}

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Function to scrape Amazon and display product image and prices
def scrape_amazon(product_name):
    # Set up the driver
    driver = webdriver.Chrome(options=chrome_options)

    # Go to Amazon
    driver.get("https://www.amazon.com")

    # Wait for the search box to be visible
    search_box = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "twotabsearchtextbox")))

    # Enter product name into the search box
    search_box.send_keys(product_name)
    search_box.send_keys(Keys.RETURN)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".a-price-whole")))

    # Find the product image
    product_image = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".s-image")))
    product_image_url = product_image.get_attribute("src")

    # Download the product image
    response = requests.get(product_image_url)
    img = Image.open(BytesIO(response.content))
    st.image(img, caption='Product Image', use_column_width=True)

    # Find all prices of the results
    prices_elements = driver.find_elements(By.CSS_SELECTOR, ".a-price-whole")

    # Convert prices to numerical values
    prices = [float(price.text.replace('$', '').replace(',', '')) for price in prices_elements]

    # Find lowest and highest prices
    lowest_price = min(prices)
    highest_price = max(prices)

    # Get user's country based on IP address
    user_country = get_user_country()

    if user_country:
        # Convert country code to currency code
        user_currency = country_to_currency.get(user_country, 'USD')
        # Convert prices to user's currency
        converted_lowest_price = convert_currency(lowest_price, 'USD', user_currency)
        converted_highest_price = convert_currency(highest_price, 'USD', user_currency)

        # Print lowest and highest prices in user's currency
        st.write("Lowest Price: ", converted_lowest_price, user_currency)
        st.write("Highest Price: ", converted_highest_price, user_currency)
    else:
        st.write("Unable to determine user's country.")

    # Close the driver
    driver.quit()

# Streamlit app layout and functionality
def main():
    st.title('أسعار منتجات أمازون')
    st.write('هذا التطبيق يقوم بجلب أسعار المنتجات من أمازون وعرضها بالعملة المحلية')

    # Request product name from the user
    product_name = st.text_input('ادخل اسم المنتج:')
    if st.button('جلب الأسعار'):
        if product_name:
            st.write(f'إليك أسعار {product_name} على أمازون:')
            # Scrape Amazon and display product image and prices
            scrape_amazon(product_name)


if __name__ == '__main__':
    main()

