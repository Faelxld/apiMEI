import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from pymongo import MongoClient
from dateutil import parser
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
import urllib.request as req
import urllib3
from pyrebase import *
import os
import sys
api_key = 'cfe54019f70ef987c0afcae6da1082ad'

def insertNuvem(json):
    db = MongoClient()['project']
    collection = db['das']       
    try: 
        dicio = {"_id":json['_id']} 
        if collection.find_one(dicio) is None:
            collection.insert(json)
            print("Novo Produto")
            print(json)
        else:
            collection.update(dicio,json)
            print("Atualizado")     
    except Exception as ex :
        print(ex)
def insertPdf(json):
    db = MongoClient()['project']
    collection = db['pdfs']
    try:
        dicio = {"_id":json['_id']}
        element = collection.find_one(dicio)
        if element is None:
            collection.insert(json)
            print("Novo Produto")
            print(json)
        else:
            json['lido'] = element['lido']
            #collection.update(dicio,json)
            print("Atualizado")
    except Exception as ex :
        print(ex)
def getCaptcha():
    captcha = open('captcha.jpg','rb')
    client = AnticaptchaClient(api_key)
    task = ImageToTextTask(captcha)
    job = client.createTask(task)
    job.join()
    return (job.get_captcha_text())

def getData(element):
    try:
        return parser.parse(element)
    except:
        return ''
def remove_repetidos(lista):
    l = []
    for i in lista:
        if i not in l:
            l.append(i)
    l.sort()
    return l

def buscaCNPJ(db):
    usuarios = db.child('Usuario').get().val()
    cnpjs = []
    for i in range(0,len(usuarios)): 
        for usuario in usuarios: 
            try:
                cnpjs.append(str(usuarios[usuario]['cnpj']))
            except:
                print('Not format')
    return remove_repetidos(cnpjs)

def initialFireBase():
    config = {
            'apiKey': "AIzaSyBIXY8s7mrDNw1V_BExArirz0FTWJoeEI4",
            'authDomain': "contabilizafacil-f5a1e.firebaseapp.com",
            'databaseURL': "https://contabilizafacil-f5a1e.firebaseio.com",
            'projectId': "contabilizafacil-f5a1e",
            'storageBucket': "contabilizafacil-f5a1e.appspot.com",
            'messagingSenderId': "545153194126"
      }
    return pyrebase.initialize_app(config)


def getTrs(soup):
    try:
        table = soup.find('table',class_='table table-hover table-condensed emissao is-detailed')
        if table is None:
            return []
        else:
            trs = table.find_all('tr')

        return trs[2:]
    except Exception as ex:
        print(ex)
        return []
def enable_download_in_headless_chrome( driver, download_dir):
    #add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    driver.execute("send_command", params)

chrome_options = Options()
chrome_options.add_argument('headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
download_dir = os.getcwd() + '/guias/'
prefs = {'download.default_directory':download_dir,
         }
chrome_options.add_experimental_option('prefs', prefs)

const = '/src/main/java/com/das/apiMEI/crawler'
print(os.getcwd() + const + "/chromedriver")
empresas = [sys.argv[1]]
jsons = []
voltar = 0
pdfs = []
for cnpj in empresas:
    try:
        url = 'http://www8.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/pgmei.app/Identificacao'
        browser = webdriver.Chrome(os.getcwd() + "/chromedriver" ,chrome_options=chrome_options)
        enable_download_in_headless_chrome(browser,download_dir)
        browser.get(url)
        captcha_input =  browser.find_element_by_xpath('/html/body/div/section/div/div/div/div/div/div[2]/form/div/div[1]/div[2]/input')
        username_box = browser.find_element_by_id('cnpj')
        username_box.send_keys(cnpj)
        login_box = browser.find_element_by_xpath('/html/body/div/section/div/div/div/div/div/div[2]/form/div/div[3]/div/button')
        captcha_fp = browser.find_element_by_id('imgCaptcha').get_attribute('src')
        req.urlretrieve(captcha_fp, "captcha.jpg")
        captcha_input.send_keys(getCaptcha())
        time.sleep(2)
        login_box.click()
        emissao = 'http://www8.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/pgmei.app/emissao'
        browser.get(emissao)
        time.sleep(3)
        combo_box = browser.find_element_by_xpath('/html/body/div/section[3]/div/div/div[1]/div/div/form/div/div/button')
        combo_box.click()
        lis = browser.find_element_by_xpath('/html/body/div/section[3]/div/div/div[1]/div/div/form/div/div/div/ul').find_elements_by_tag_name('li')
        anos = len(lis)
        json = {'_id': cnpj,
                "cnpj":cnpj,
                'das':[],
                }
        for i in range(0,anos):
            guias = []
            try:
                lis = browser.find_element_by_xpath('/html/body/div/section[3]/div/div/div[1]/div/div/form/div/div/div/ul').find_elements_by_tag_name('li')
                li = lis[i]
                voltar = li
                combo_box = browser.find_element_by_xpath('/html/body/div/section[3]/div/div/div[1]/div/div/form/div/div/button')
                ButtonOk = browser.find_element_by_xpath('/html/body/div/section[3]/div/div/div[1]/div/div/form/button')
                time.sleep(4)
                combo_box.click()
                time.sleep(4)
                li.click()
                ButtonOk.click()
                html = browser.page_source
                soup = BeautifulSoup(html, 'html.parser')
                trs = soup.find('table',class_='table table-hover table-condensed emissao is-detailed').find_all('tr')
                trs = trs[2:]
            except:
                continue
            for tr in trs:
                tds = tr.find_all('td')
                ano = tds[1].text.split('/')[1]
                guia = {
                    'Periodo':tds[1].text,
                    'Apurado': tds[2].text.replace('\n','').replace(' ',''),
                    'INSS':tds[3].text.replace('\n','').replace(' ',''),
                    'Principal':tds[5].text.replace('R$','').replace(' ',''),
                    'Multa':tds[6].text.replace('R$','').replace(' ',''),
                    'Juros':tds[7].text.replace('R$','').replace(' ',''),
                    'Total':tds[8].text.replace('R$','').replace(' ',''),
                    'Data_Vencimento':getData(tds[9].text),
                    'Data_Acolimento':getData(tr.find('td',class_='acolhimento updatable text-center').text),


                }
                guias.append(guia)
            pdf = {"ano":ano,
                  'link':None,
                 'cnpj': cnpj,
                 '_id': None,
                  'lido': False,
                   'partial': False
            }

            try:
                os.system('sudo rm guias/*.pdf')
                json['das'].append(guias)
                time.sleep(2)
                check_box = browser.find_element_by_id('selecionarTodos')
                check_box.click()
                buttonEmitir = browser.find_element_by_id('btnEmitirDas')
                buttonEmitir.click()
                time.sleep(3)
                buttonImprimir = browser.find_element_by_xpath('/html/body/div[1]/section[3]/div/div/div[1]/div/div/div[3]/div/div/a[1]')
                buttonImprimir.click()
                time.sleep(6)
                firebase = initialFireBase()
                storage = firebase.storage()
                arquivo = os.listdir(os.getcwd() + '/guias')
                print(arquivo[0])
                os.rename(os.getcwd() + '/guias/' + arquivo[0], os.getcwd() + '/guias/' +cnpj + '-' + ano + '.pdf')
                arquivo = os.listdir(os.getcwd() + '/guias')
                time.sleep(2)
                results = storage.child("cpnj/das/" +  arquivo[0]).put(os.getcwd() + '/guias/' + arquivo[0])
                pdf['link'] = storage.child("cpnj/das/" +  arquivo[0]).get_url()
                pdf['_id'] =  pdf['cnpj'] + '-' + pdf['ano']
                insertPdf(pdf)
                browser.get(emissao)
                time.sleep(3)
                os.system('sudo rm guias/*.pdf')
            except Exception as ex:
                print(ex)
        jsons.append(json)
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
for json in jsons:
    insertNuvem(json)

os.system('sudo rm guias/*.pdf')
