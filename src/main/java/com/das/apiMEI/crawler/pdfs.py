from PyPDF2 import PdfFileReader, PdfFileWriter
import urllib
import os
from pyrebase *
from pymongo import MongoClient



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
    firebase = pyrebase.initialize_app(config)

    db = firebase.database()

    return db
def download_file(download_url,name):
    response = urllib.request.urlopen(download_url)
    file = open(os.getcwd() + '/separados/'+ name + ".pdf", 'wb')
    file.write(response.read())
    file.close()
    print("Completed")
def filtrarAno(lista):
    filtro = []
    for li in lista:
        for item in li:
            if item['Apurado'] == 'Sim':
                filtro.append(item)
    return filtro
def montaMes(das,cnpj):
    lista = []
    i = 0
    for item in das:
        lista.append(cnpj +'-' + str(i))
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
das = list(db['das'].find())
for item in das:
    try:
        os.system("sudo rm processados/*.pdf")
        os.system("sudo rm separados/*.pdf")
        cnpj = item['cnpj']
        listaDas = item['das']
        for ds in listaDas:
            try:
                os.system("sudo rm processados/*.pdf")
                os.system("sudo rm separados/*.pdf")
                act_sub_pages_name = []
                ano = ds[0]['Periodo'].split('/')[1]
                print(ds[0]['Periodo'])
                act_sub_pages_name = montaMes(ds,cnpj) 
                pdf = list(collection.find({'cnpj':cnpj,'ano': ano ,'lido':False}))[0]
                print(pdf)
                name = cnpj + '-' + ano
                download_file(pdf['link'], name )
                act_pdf_file = os.getcwd() + '/separados/' + name + '.pdf'
                reader = PdfFileReader(act_pdf_file)
                print(len(act_sub_pages_name))
                for x in range(reader.getNumPages()): 
                    print(x)
                    pdf_splitter(x, act_pdf_file)

                i = 0
                for item in ds:
                    try:
                        firebase = initialFireBase()
                        storage = firebase.storage()
                        arquivos = os.listdir(os.getcwd() + '/processados')
                        arqvPdf = {"Periodo":item['Periodo'],
                        'link':None,
                        'cnpj': cnpj,
                        '_id': None,
                        'lido': True,
                        'partial': True
                        }
                        results = storage.child("cpnj/das").put(os.getcwd() + '/processados/' + arquivos[i])
                        arqvPdf['link'] = "https://firebasestorage.googleapis.com/v0/b/contabilizafacil-f5a1e.appspot.com/o/cpnj%2Fdas?alt=media&token=" + results['downloadTokens']
                        arqvPdf['_id'] =  arqvPdf['cnpj'] + '-' + arqvPdf['Periodo'].replace('/','-')
                        print(arqvPdf)
                        insertPdf(arqvPdf)
                        pdf['lido'] = True
                        #collection.update({'_id':pdf['_id']},pdf)
                        i = i + 1
                    except Exception as ex:
                        print(ex)
    
            except Exception as ex:
                print(ex)

            finally:
                os.system("sudo rm processados/*.pdf")
                os.system("sudo rm separados/*.pdf")
    except Exception as ex:
        print(ex)