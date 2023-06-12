import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('https://www.example.com')

# Find the target element to move the mouse over
target_element = driver.find_element(By.XPATH, '//a')

print(target_element)

# Create an instance of ActionChains
actions = ActionChains(driver)

# Move the mouse to the target element
actions.move_to_element(target_element)

# Perform the action to move the mouse
actions.perform()
time.sleep(3)  

# Optional: Add additional mouse movements like dragging, clicking, etc.
# actions.drag_and_drop(source_element, target_element).perform()
actions.click().perform()
time.sleep(1000)  

driver.quit()
