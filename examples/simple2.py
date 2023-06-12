import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait


class WindowClosedManually:
    def __call__(self, driver):
        try:
            # Attempt to switch to the window, if it fails, it means the window was closed
            #driver.switch_to.window(driver.window_handles[0])
            driver.title
            return False
        except:
            return True


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.get( 'https://nowsecure.nl' )

    window_closed_manually = WindowClosedManually()
    WebDriverWait(driver, 10000).until(window_closed_manually)
