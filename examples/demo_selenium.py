# -*- coding: utf-8 -*-
# Time       : 2022/9/23 17:28
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import time
import typing
import sys
import random
import json 
import re 
import os
sys.path.append('../')

from selenium.common.exceptions import (
    ElementNotInteractableException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import hcaptcha_challenger as solver
from hcaptcha_challenger import HolyChallenger
from hcaptcha_challenger.exceptions import ChallengePassed

# Existing user data
email = "plms-123@tesla.com"
country = "Hong Kong"
headless = False
nfeKey = '35230502559428000366550000000298401713145195'

# Init local-side of the ModelHub
solver.install()


def hit_challenge(ctx, challenger: HolyChallenger, retries: int = 10) -> typing.Optional[str]:
    """
    Use `anti_checkbox()` `anti_hcaptcha()` to be flexible to challenges
    :param ctx:
    :param challenger:
    :param retries:
    :return:
    """
    print('HIT CHALLENGE')
    if challenger.utils.face_the_checkbox(ctx):
        print('FACE THE CHECKBOX')
        time.sleep(random.uniform(0.2, 0.5))
        challenger.anti_checkbox(ctx)
        time.sleep(random.uniform(0.3, 1))
        if res := challenger.utils.get_hcaptcha_response(ctx):
            print('RESPONSE = {}'.format(res))
            return res
    else:
        print('CLICK CHECKBOX')
        challenger.anti_checkbox(ctx)

    for ix in range(retries):
        try:
            print('trying again {} for {} times'.format(ix, retries))
            time.sleep(random.uniform(0.3, 1))
            if (resp := challenger.anti_hcaptcha(ctx)) is None:
                continue
            if resp == challenger.CHALLENGE_SUCCESS:
                print('RESPONSE = {}'.format(resp))
                time.sleep(random.uniform(0.3, 1))
                return challenger.utils.get_hcaptcha_response(ctx)
        except ChallengePassed:
            time.sleep(random.uniform(0.3, 1))
            return challenger.utils.get_hcaptcha_response(ctx)
        challenger.utils.refresh(ctx)
        time.sleep(random.uniform(0.2, 0.5))
    return None


def bytedance():
    # New Challenger
    challenger = solver.new_challenger(screenshot=True, debug=True)

    # Replace selenium.webdriver.Chrome with CTX
    ctx = solver.get_challenge_ctx(silence=headless)
    ctx.get("https://dashboard.hcaptcha.com/signup")
    try:
        # Populate test data
        WebDriverWait(ctx, 15, ignored_exceptions=(ElementNotInteractableException,)).until(
            EC.presence_of_element_located((By.ID, "email"))
        ).send_keys(email)
        WebDriverWait(ctx, 15, ignored_exceptions=(ElementNotInteractableException,)).until(
            EC.presence_of_element_located((By.ID, "country"))
        ).send_keys(country)
        # Handling context validation
        resp = hit_challenge(ctx=ctx, challenger=challenger)
        print('CHALLENGE RESPONSE = {}'.format(resp))
        # Submit test data
        WebDriverWait(ctx, 5, ignored_exceptions=(ElementClickInterceptedException,)).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-cy]"))
        ).click()

        ctx.save_screenshot(f"datas/bytedance{' - headless' if headless else ''}.png")
    finally:
        ctx.quit()


class WindowClosedManually:
    def __call__(self, driver):
        try:
            # Attempt to switch to the window, if it fails, it means the window was closed
            #driver.switch_to.window(driver.window_handles[0])
            driver.title
            return False
        except:
            return True

def getTableFormat1(rows):
    data = {}
    rowcnt = 0
    index = []
    for row in rows:
        cols = row.find_elements(By.XPATH, './/td')
        colcnt = 0
        for col in cols:
            if rowcnt == 0:
                index.append(col.find_element(By.XPATH, './/label').get_attribute("innerHTML").strip())
            else:
                data[index[colcnt]] = col.find_element(By.XPATH, './/span').get_attribute("innerHTML").strip()
            colcnt = colcnt + 1
        rowcnt = rowcnt + 1
    return data

def getTableFormat2(fieldset, label):
    data = {}
    fields = fieldset.find_elements(By.XPATH, './/td')
    for field in fields:
        try:
            print('FIELD = {}'.format(field.get_attribute("innerHTML")))
            fieldname = field.find_element(By.XPATH, './/label').get_attribute("innerHTML").strip()
            fieldvalue = field.find_element(By.XPATH, './/span').get_attribute("innerHTML").strip()
            data[fieldname] = fieldvalue
        except NoSuchElementException as ex:
            #print(ex)
            print('FIELD {} DOUBLE CHECK THIS DATA {}'.format(label, field.get_attribute("innerHTML")))
    return data

def getTableFormat3(fieldset):
        
    data = {}
    rowcnt = 0
    index = [] # column index
    tablecnt = 0
    for row in fieldset.find_elements(By.XPATH, './/table'):
        if tablecnt == 0:
            # table headers 
            print('HEADER = {}'.format(row.get_attribute('class')))
            cols = row.find_elements(By.XPATH, './/td')
            for col in cols:
                index.append(col.get_attribute("innerHTML").strip())
        elif tablecnt == 1:
            # payment formats 
            print('HEADER = {}'.format(row.get_attribute('class')))
            payments = row.find_elements(By.XPATH, './/tr')
            paymentNo = 0
            data['payments'] = []
            for payment in payments:
                # get payment detail 
                paymentData = {}
                _i = 0
                for paymentInfo in payment.find_elements(By.XPATH, '//td/span'):
                    paymentData[index[_i]] = paymentInfo.get_attribute("innerHTML").strip()
                data['payments'].append(paymentData)
        elif tablecnt == 2:
            # payment detail complement
            print('HEADER = {}'.format(row.get_attribute('class')))
        tablecnt = tablecnt + 1
    return data


def saveNFE(ctx, content, nfeKey, _format='html'):
    # print(content)
    data = ''
    if _format == 'json':

        data = {}
        elements = content.find_elements(By.XPATH, '//div[@class="nft"]')

        for element in elements:
            print(' >>>>> NEXT ELEMENT ID = {}<<<<<<<'.format(element.get_attribute('id')))

            fieldsets = element.find_elements(By.XPATH, './/fieldset')

            print(fieldsets)

            for fieldset in fieldsets:
                label = fieldset.find_element(By.XPATH, './legend').get_attribute("innerHTML").strip()
                #print('FIELDSET INNERHTML = {}'.format(fieldset.find_element(By.XPATH, './legend').get_attribute("innerHTML")))

                data[label] = {}

                print('>>> GETTING DATA FOR "{}"'.format(label))

                if 'Situação Atual:' in label:
                    # little different table structure (header / row)

                    #_data = re.split(r'Situação Atual:\n(.*)\n(Ambiente de autorização:\n(.*)\)', label)
                    _data = re.search(r'Situação Atual:\s+(.*)\s+\(Ambiente de autorização:\s+(.*)\)', label.replace('\n', '').strip()).groups()
                    status = _data[0].strip()
                    environment = _data[1].strip()

                    data.pop(label) # remove previous label ...

                    label = 'Situacao'
                    data[label] = {} 

                    data[label]['status'] = status
                    data[label]['environment'] = environment

                    rows = fieldset.find_elements(By.XPATH, './/tr')

                    data[label]['info'] = getTableFormat1(rows)

                else:
                    if 'Formas de Pagamento' in label:
                        print('>>>>> GET {} FORMAT 3'.format(label))
                        x = getTableFormat3(fieldset)
                        print(json.dumps(x))
                        data[label] = x
                        pass
                    else:
                        print('>>>>> GET {} FORMAT 2'.format(label))
                        x = getTableFormat2(fieldset, label)
                        print(json.dumps(x))
                        data[label] = x

        data['chave'] = nfeKey
        data = json.dumps(data, indent=4)
    else:
        data = ctx.execute_script("return arguments[0].innerHTML;",content)
        data = '<div id="NFe">{}</div>'.format(data)


    if not os.path.exists('datas/docs'):
        os.makedirs('datas/docs')

    with open('datas/docs/nfe-{}.{}'.format(nfeKey, _format), 'w') as f:
        f.write(data)
        f.flush()
        f.close()

def nfe():
    # New Challenger
    challenger = solver.new_challenger(screenshot=True, debug=True, lang="pt", onnx_prefix="YOLOv6n")

    # Replace selenium.webdriver.Chrome with CTX
    ctx = solver.get_challenge_ctx(silence=headless)
    ctx.get("https://www.nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx?tipoConsulta=resumo") # &tipoConteudo=7PhJ+gAVw2g=
    try:
        # Populate test data
        element = WebDriverWait(ctx, 15, ignored_exceptions=(ElementNotInteractableException,)).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtChaveAcessoResumo"))
        )
        cleanup = WebDriverWait(ctx, 15, ignored_exceptions=(ElementNotInteractableException,)).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_btnLimparHCaptcha"))
        )
        actions = ActionChains(ctx)
        actions\
            .move_to_element(element)\
            .pause(random.uniform(0.2, 0.8))\
            .click()\
            .pause(random.uniform(0.5, 1))\
            .send_keys(nfeKey)\
            .pause(random.uniform(0.5, 1))\
            .move_to_element(cleanup)\
            .perform()
        #time.sleep(random.uniform(0.2, 0.5))  
        #element.click()
        #time.sleep(random.uniform(0.2, 0.3))
        #element.send_keys(nfeKey)
        # Handling context validation
        success = hit_challenge(ctx=ctx, challenger=challenger)
        # Submit test data
        if success is not None:

            print('SUCCESS = {}'.format(success))

            # xpath = "//textarea[@name='h-captcha-response']"
            # el = ctx.find_element(By.NAME, "h-captcha-response")
            # ctx.execute_script("arguments[0].removeAttribute('style')", el)
            # print('el = {}'.format(el))
            
            # el.send_keys(success)
            cnt = 10
            while cnt > 0:

                cnt = cnt - 1

                print('try click continue #{}'.format(cnt))

                xpath = "//input[@value='Continuar']"
                #target_element = ctx.execute_script("return document.evaluate(\"{}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;".format(xpath))
                target_element = ctx.find_element(By.XPATH, xpath)

                print('target_element = {}'.format(target_element))
                actions = ActionChains(ctx)

                actions\
                    .move_to_element(target_element)\
                    .pause(random.uniform(1, 2))\
                    .click()\
                    .perform()
                time.sleep(3)  

                try:
                    err = WebDriverWait(ctx, 5, ignored_exceptions=(ElementNotInteractableException,)).until(
                        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_bltMensagensErroHCaptcha"))
                    )

                    if err is not None: 
                        print('ERROR = {}'.format(err))
                        print('TRY AGAIN CLICK THE CHECKBOX')
                        time.sleep(random.uniform(1, 2))
                        if challenger.anti_checkbox(ctx):
                            continue
                        else:
                            print('UPS .... do the challenge again')
                except TimeoutException as ex:
                    print('SUCCESS')
                    content = WebDriverWait(ctx, 5, ignored_exceptions=(ElementNotInteractableException,)).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "aba_container"))
                    )
                    saveNFE(ctx, content, nfeKey)
                    saveNFE(ctx, content, nfeKey, 'json')
                
                    ctx.save_screenshot(f"datas/nfe{' - headless' if headless else ' - result'}.png")
                    #time.sleep(100)
                    break 

            #actions.click().perform()

            # success2 = hit_challenge(ctx=ctx, challenger=challenger)
            # print('SUCCESS2 = {}'.format(success2))

            # xpath = "//input[@value='Continuar']"
            # target_element = ctx.execute_script("return document.evaluate(\"{}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;".format(xpath))

            # print('target_element = {}'.format(target_element))
            # actions = ActionChains(ctx)

            # actions\
            #     .move_to_element(target_element)\
            #     .pause(random.uniform(1, 2))\
            #     .click()\
            #     .perform()

            # WebDriverWait(ctx, 15, ignored_exceptions=(ElementClickInterceptedException,)).until(
            #     #EC.element_to_be_clickable((By.XPATH, "//button[@data-cy]"))
            #     EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']"))
            # ).click()

            # ctx.save_screenshot(f"datas/nfe{' - headless' if headless else ' - result'}.png")

        # DEBUG --- TURN ON/OFF TO DOUBLE CHECK THE RESULT
        # window_closed_manually = WindowClosedManually()
        # WebDriverWait(ctx, 10000).until(window_closed_manually)


    finally:
        ctx.quit()


def sample():
    # New Challenger
    challenger = solver.new_challenger(screenshot=True, debug=True, lang="pt", onnx_prefix="YOLOv6n")

    # Replace selenium.webdriver.Chrome with CTX
    ctx = solver.get_challenge_ctx(silence=headless)
    ctx.get("https://2captcha.com/demo/hcaptcha")
    try:
        # Populate test data
        success = hit_challenge(ctx=ctx, challenger=challenger)
        # Submit test data
        if success is not None:

            xpath = "//button[text()='Check']"
            target_element = ctx.execute_script("return document.evaluate(\"{}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;".format(xpath))

            print('target_element = {}'.format(target_element))
            actions = ActionChains(ctx)

            actions.move_to_element(target_element).perform()
            time.sleep(3)  

            actions.click().perform()


            # WebDriverWait(ctx, 15, ignored_exceptions=(ElementClickInterceptedException,)).until(
            #     #EC.element_to_be_clickable((By.XPATH, "//button[@data-cy]"))
            #     EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']"))
            # ).click()

            #ctx.save_screenshot(f"datas/nfe{' - headless' if headless else ' - result'}.png")

        window_closed_manually = WindowClosedManually()
        WebDriverWait(ctx, 10000).until(window_closed_manually)


    finally:
        ctx.quit()


if __name__ == "__main__":
    bytedance()
