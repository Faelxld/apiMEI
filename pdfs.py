from PyPDF2 import PdfFileReader, PdfFileWriter
import urllib
import os
from pyrebase import *
from pymongo import MongoClient
import sys


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
            collection.update(dicio,json)
            print("Atualizado")
    except Exception as ex :
        print(ex)
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
def download_file(download_url,name):
    response = urllib.request.urlopen(download_url)
    file = open(os.getcwd() + '/separados/'+ name + ".pdf", 'wb')
    file.write(response.read())
    file.close()
    print("Completed")
def filtrarAno(lista):
    filtro = []
    for li in lista:
        if li['Apurado'] == 'Sim':
            filtro.append(item)
    return filtro
def montaMes(das,cnpj,ano):
    lista = []
    i = 0
    for item in das:
        lista.append(cnpj + '-' + item['Periodo'].replace('/','-') + '-' + ano + '.pdf')
        i = i + 1
    return lista

def pdf_splitter(index, src_file):
    with open(src_file, 'rb') as act_mls:
        reader = PdfFileReader(act_mls)
        writer = PdfFileWriter()
        writer.addPage(reader.getPage(index))
        const = os.getcwd() + '/processados/'
        out_file = os.path.join(const, act_sub_pages_name[index])
        with open(out_file, 'wb') as out_pdf: writer.write(out_pdf)


db = MongoClient()['project']
collection = db['pdfs']
das = list(db['das'].find({'cnpj':sys.argv[1]}))
collection.remove({'partial':True,'cnpj':sys.argv[1]})
for item in das:
    try:
        os.system('find '+  os.getcwd()+ '/processados' + ' -name '  + cnpj + '-exec rm -f {} \;')
        os.system('find '+  os.getcwd()+ '/separados' + ' -name '  + cnpj + '-exec rm -f {} \;')

        cnpj = item['cnpj']
        listaDas = item['das']
        for ds in listaDas:
            try:
                act_sub_pages_name = []
                apurados = []
                for dsl in ds:
                    try:
                        #os.system("sudo rm processados/*.pdf")
                        #os.system("sudo rm separados/*.pdf")
                        ano = dsl['Periodo'].split('/')[1]
                        print(dsl['Periodo'])
                        if dsl['INSS'] == 'AVencer':
                            apurados.append(dsl)
                            act_sub_pages_name.append(cnpj + '-' + dsl['Periodo'].replace('/','-') + '.pdf')
                    except Exception as ex:
                        print(ex)
                print(act_sub_pages_name )
                pdf = list(collection.find({'cnpj':cnpj,'ano': ano}))[0]
                name = cnpj + '-' + ano
                download_file(pdf['link'], name )
                act_pdf_file = os.getcwd() + '/separados/' + name + '.pdf'
                reader = PdfFileReader(act_pdf_file)
                print(len(act_sub_pages_name))
                for x in range(reader.getNumPages()):
                    print(x)
                    pdf_splitter(x, act_pdf_file)
                for dsll in apurados:
                    try:
                        firebase = initialFireBase()
                        storage = firebase.storage()
                        arqvPdf = {"Periodo":dsll['Periodo'],
                        'link':None,
                        'cnpj': cnpj,
                        '_id': None,
                        'lido': True,
                        'partial': True
                        }
                        arquivo = cnpj + '-' + dsll['Periodo'].replace('/','-') + '.pdf'
                        results = storage.child("cpnj/das/" + arquivo).put(os.getcwd() + '/processados/' + arquivo)
                        arqvPdf['link'] = storage.child("cpnj/das/" + arquivo).get_url(None)
                        arqvPdf['_id'] =  arqvPdf['cnpj'] + '-' + arqvPdf['Periodo'].replace('/','-')
                        print(arqvPdf)
                        insertPdf(arqvPdf)
                    except Exception as ex:
                        print(ex)


            except Exception as ex:
                print(ex)
            finally:
                os.system('sudo rm processados/*'+cnpj+ '*')
                os.system('sudo rm separados/*'+cnpj+ '*')

    except Exception as ex:
        print(ex)