import requests as rq
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from pymongo import MongoClient
from dateutil import parser
from dateutil import parser
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
import urllib.request as req
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
        if collection.find_one(dicio) is None:
            collection.insert(json)
            print("Novo Produto")
            print(json)
        else:
            collection.update(dicio,json)
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
    firebase = pyrebase.initialize_app(config)

    db = firebase.database()

    return db

 
            
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
prefs = {'download.default_directory' : os.getcwd() + '/guias'}
chrome_options.add_experimental_option('prefs', prefs)

const = '/src/main/java/com/das/apiMEI/crawler'
print(os.getcwd() + const + "/chromedriver")
empresas = [sys.argv[1]]
jsons = []
for cnpj in empresas:
    try:
        url = 'http://www8.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/pgmei.app/Identificacao'
        browser = webdriver.Chrome(os.getcwd() +  "/chromedriver" ,chrome_options=chrome_options)
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
                'das':None,
                'pdfs':None
                }
        pdfs = []
        for i in range(0,anos):
            guias = []
            try:
                lis = browser.find_element_by_xpath('/html/body/div/section[3]/div/div/div[1]/div/div/form/div/div/div/ul').find_elements_by_tag_name('li')
                li = lis[i]
                time.sleep(2)
                combo_box = browser.find_element_by_xpath('/html/body/div/section[3]/div/div/div[1]/div/div/form/div/div/button')
                ButtonOk = browser.find_element_by_xpath('/html/body/div/section[3]/div/div/div[1]/div/div/form/button')
                time.sleep(2)
                combo_box.click()
                time.sleep(2)
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
                pdf = {"ano":tds[1].text.split('/')[1],
                       'link':None,
                       'cnpj': cnpj,
                       '_id': None
                       }
                guia = {
                    'Periodo':tds[1].text,
                    'Apurado': tds[2].text.replace('\n','').replace(' ',''),
                    'INSS':tds[3].text.replace('\n','').replace(' ',''),
                    'Principal':tds[4].text.replace('R$','').replace(' ',''),
                    'Multa':tds[5].text.replace('R$','').replace(' ',''),
                    'Juros':tds[6].text.replace('R$','').replace(' ',''),
                    'Total':tds[7].text.replace('R$','').replace(' ',''),
                    'Data_Vencimento':getData(tds[8].text),
                    'Data_Acolimento':getData(tds[9].text)

                   }
                guias.append(guia)
            pdfs.append(pdf)
            time.sleep(5)
            check_box = browser.find_element_by_id('selecionarTodos')
            check_box.click()
            buttonEmitir = browser.find_element_by_id('btnEmitirDas')
            buttonEmitir.click()
            time.sleep(5)
            buttonImprimir = browser.find_element_by_xpath('/html/body/div[1]/section[3]/div/div/div[1]/div/div/div[3]/div/div/a[1]')
            buttonImprimir.click()
            time.sleep(5)
            browser.get(emissao)           
            json['das'] = guias
        jsons.append(json)

    except Exception as ex:
        print(ex)
    finally:
        browser.close()
for json in jsons:
    insertNuvem(json)

arquivos = os.listdir(os.getcwd() + '/guias')
firebase = initialFireBase()
storage = firebase.storage()
for i in range(0,len(pdfs)):
    results = storage.child("cpnj/das").put(os.getcwd() + '/guias/' + arquivos[i])
    pdfs[i]['link'] = "https://firebasestorage.googleapis.com/v0/b/contabilizafacil-f5a1e.appspot.com/o/cpnj%2Fdas?alt=media&token=" + results['downloadTokens']
    pdfs[i]['_id'] = results['downloadTokens']


os.system("rm " + os.getcwd() + '/guias/*.pdf')

for pdf in pdfs:
    insertPdf(pdf)