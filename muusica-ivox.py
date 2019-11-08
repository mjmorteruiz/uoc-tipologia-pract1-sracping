import requests
import lxml
import bs4
import argparse
import os
import csv
import sys
import pathlib



tipos_muusica={
"all":"Todo tipo de múscia",
"a" :"Alternativa e indie",
"b" :"Blues y Jazz",
"e" :"Electrónica",
"p" :"Pop y Pop-Rock",
"r" :"Rock y Metal",
"bs"  :"BSO y Clásica",
"h" :"Hip Hop y Rap",
"s" :"Soul, Funk y R&B",
"m" :"Músicas del mundo y otras",
"ex":"Experimental y new age"
}

tipos_url_base={
"all":"https://www.ivoox.com/audios-musica_sa_f311_1.html",
"a":"https://www.ivoox.com/audios-alternativa-e-indie_sa_f462_1.html",
"b" :"https://www.ivoox.com/audios-blues-jazz_sa_f463_1.html",
"e" :"https://www.ivoox.com/audios-electronica_sa_f464_1.html",
"p" : "https://www.ivoox.com/audios-pop-pop-rock_sa_f465_1.html",
"r" : "https://www.ivoox.com/audios-rock-metal_sa_f466_1.html",
"bs": "https://www.ivoox.com/audios-bso-clasica_sa_f467_1.html",
"h" :"https://www.ivoox.com/audios-hip-hop-rap_sa_f468_1.html",
"s" :"https://www.ivoox.com/audios-soul-funk-r-b_sa_f470_1.html",
"m" :"https://www.ivoox.com/audios-musicas-del-mundo-otras_sa_f471_1.html",
"ex":"https://www.ivoox.com/audios-experimental-new-age_sa_f472_1.html"
}


#Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--tipo", help='''Elige el tipo de música:
"a":"Alternativa e indie",
"b":"Blues y Jazz",
"e":"Electrónica",
"p":"Pop y Pop-Rock",
"r":"Rock y Metal",
"bs":"BSO y Clásica",
"h":"Hip Hop y Rap",
"s":"Soul, Funk y R&B",
"m":"Músicas del mundo y otras",
"ex":"Experimental y new age"

 ''')
args = parser.parse_args()

t=args.tipo

if not t:
  print("Debes elegir tipo de música: ejemplo: >python muusica-ivox.py --tipo a")
  exit()

if t in tipos_muusica:
  print("Has elegido: {}".format(tipos_muusica[t]))
else:
  print("La opción elegeda no es correcta")
  exit()





#función para generar las url correspondientes con la paginación del sitio web:
def genera_paag(url, j):
  partes=url.split('_')
  s=""
  for i in range(len(partes)-1):
    s=s+partes[i]+"_"
  s=s+str(j)+".html"
  return s


#FUNCIONES DE OBTENCÍON DEL DATASET A PARTIR DEL DIV CONTENDDOR, LLAMADO 'marco'
def obtener_caraatula(marco):#cada marco tiene 2 imágenes, y la carátula es la primera

    imgs=marco.select('img')    #obtiene 2 imágenes
    im=imgs[0]                  #guarda la primera
    return(im['src'])           #saca el vínculo

def obtener_programa (marco):#es un tag 'a' dentro del div con class='wrapper'
    divs=marco.select('div')
    for d in divs:
        if d.has_attr('class') and d['class'][0]=='wrapper':
            a=d.select('a')
            tag=a[0]
            return(tag['title'])

def obtener_emisioon(marco):#está dentro de un 'p' con class="title-wrapper text-ellipsis-multiple"
    ps=marco.select('p')
    for p in ps:
        if p.has_attr('class'):
            c=p['class']
            if len(c)==2 and 'title-wrapper' in c and 'text-ellipsis-multiple' in c:
                aas=p.select('a')
                tag=aas[0]
                return (tag['title'])

def obtener_tiempo(marco):# p.time
    ps=marco.select('p')
    for p in ps:
        if p.has_attr('class') and 'time' in p['class']:
            return (p.getText())

def obtener_tipo_muusica(marco):# busco a.rounded-label
    aa=marco.select('a')
    for a in aa:
        if a.has_attr('class') and 'rounded-label' in a['class']:
            return (a.getText()).strip()

def obtener_likes(marco):# busco li.likes y dentro un a con 'title'="r'\d' Likes"
    lis=marco.select('li')
    for li in lis:
        if li.has_attr('class') and 'likes' in li['class']:
            texto=li.a['title']
            texto=texto.split(" ")[0]
            return texto


def obtener_comentarios(marco): # busco li.comments y dentro un a con 'title'="r'\d' Comentarios"
   lis=marco.select('li')
   for li in lis:
       if li.has_attr('class') and 'comments' in li['class']:
           texto=li.a['title']
           texto=texto.split(" ")[0]
           return texto

def obtener_diias(marco):#li.date getText()
    lis=marco.select('li')
    for li in lis:
        if li.has_attr('class') and 'date' in li['class']:
            texto=li.getText()
            texto=texto.strip()
            return texto

def obtener_reproducir(marco):# busco div.play , dentro el 'a' con rel="nofollow" y onclick="...."
  divs=marco.select('div')
  for div in divs:
    if div.has_attr("class") and 'play' in div["class"]:
        aas=div.select('a')
        for a in aas:
          if a.has_attr("rel") and a.has_attr("onclick") and 'nofollow' in a["rel"]:
            link=a["onclick"]
            link=link.split('"')[1]
            return link


url_base=tipos_url_base[t]


lista=[]
encabezado= ['Carátula', 'Programa', 'Emisión', 'Tiempo', 'Tipo de música', 'Likes', 'Comentarios','Antigüedad', 'Reproducir']
lista.append(encabezado)


npags=5 #se recomienda poner 20 como máximo
for i in range(npags):
  url=genera_paag(url_base,1+i)

  #proceso la página
  res=requests.get(url)
  soup=bs4.BeautifulSoup(res.text,'lxml')
  div=soup.select('div')

  marcos=[]
  #filtro los div que tienen class="front modulo-view modulo-type-episodio"
  for d in div:
      if d.has_attr('class'):
          c= (d['class'])
          if len(c)==3 and 'front' in c and 'modulo-view' in c and 'modulo-type-episodio' in c:
              marcos.append(d)




  #por cada marco saco una fila del dataset
  for m in marcos:
    fila=[]
    fila.append(obtener_caraatula(m))
    fila.append(obtener_programa(m))
    fila.append(obtener_emisioon(m))
    fila.append(obtener_tiempo(m))
    fila.append(obtener_tipo_muusica(m))
    fila.append(obtener_likes(m))
    fila.append(obtener_comentarios(m))
    fila.append(obtener_diias(m))
    fila.append(obtener_reproducir(m))

    lista.append(fila)

  print("Procesada la página {} de {}... ".format(1+i,npags))





#escritura
currentDir = pathlib.Path(__file__).parent
filename = " "
filePath = os.path.join(currentDir, filename)

with open(filePath,'w',newline='') as csvFile:
  writer=csv.writer(csvFile)
  for l in lista:
    writer.writerow(l)

print("Se ha creado el fichero {} en la ruta: {}".format(filename,filePath))


