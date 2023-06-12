#from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait



class WindowClosedManually:
    def __call__(self, driver):
        try:
            # Attempt to switch to the window, if it fails, it means the window was closed
            driver.switch_to.window(driver.window_handles[0])
            return False
        except:
            return True



# Create a new ChromeDriver instance
#driver = webdriver.Chrome()
# options = uc.ChromeOptions()
# options.headless = True
# options.add_argument( '--headless' )
# chrome = uc.Chrome( options = options )

driver = uc.Chrome()

# Navigate to a webpage
driver.get("https://www.google.com")


window_closed_manually = WindowClosedManually()
WebDriverWait(driver, 10000).until(window_closed_manually)

# Perform actions or extract information from the webpage
# ...

# Quit the browser
driver.quit()

if __name__ == '__main__':
    freeze_support()