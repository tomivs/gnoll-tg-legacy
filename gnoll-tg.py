#!/usr/bin/python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE, STDOUT
from random import randint
import urllib2, json, re, sys
# recargamos el módulo «sys» y definimos «utf-8» por defecto
reload(sys)
sys.setdefaultencoding("utf-8")

# esto se debe cambiar segun esté instalado el telegram-cli
p = Popen(['/ruta/o/comando/a/telegram-cli', '--json','-k', '/ruta/para/tg-server.pub'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)

# definimos las variables para evitar flood
flood = False
cancion = ''

# esta función es la que elimina carácteres "basura" del texto o «string» que recibimos
def limpiar(texto):
    texto = texto.replace('\x1b[K>', '')
    texto = texto.replace('\x1b[K', '')
    texto = texto.replace('>', '', 1)
    return texto

# esta función envía los comandos que se le ordenen y retorna un valor «True» o «False» según se ha procesado
def enviar(texto, var_popen):
    # enviamos el texto
    var_popen.stdin.write(texto)
    # leemos la respuesta que nos da
    while True:
        respuesta = limpiar ( var_popen.stdout.readline() )
        respuesta_decodeada = decodear(respuesta)
        if respuesta_decodeada != False:
            try:
                if respuesta_decodeada['result'] == 'SUCCESS':
                    return True
                    break
                elif respuesta_decodeada['result'] == 'FAIL':
                    return False
                    break
            except:
                pass

# esta funcion intenta decodificar el texto en JSON o en su lugar retorna «False»
def decodear(texto):
    try:
        decodeado = json.loads(texto)
    except:
        decodeado = False
        pass
    return decodeado

while p.poll() is None:
    # limpiamos los carácteres basura
    texto = limpiar ( p.stdout.readline() )
    # intentamos decodificar en formato JSON
    recibido = decodear(texto)
    
    # si recibimos algo en formato JSON
    if recibido:
        # mostramos en consola lo que recibimos (esto es opcional)
        print recibido
        
        # aquí vamos a darnos cuenta si lo que recibimos es solo texto (puede ser multimedia)
        try:
            if recibido['text'] != '':
                solo_texto = True
        except KeyError:
            solo_texto = False
        
        # si lo que recibimos es un mensaje y es solo texto
        if recibido['event'] == 'message' and solo_texto:
            
            # evaluamos si el bot es nombrado y damos una respuesta
            if recibido['text'].lower().find('gnoll') != -1 or recibido['text'].lower().find('bot') != -1 or recibido['text'].lower().find('dolartoday') != -1:
                archivo = open('nombrado.txt').readlines()
                palabra = randint(0, len(archivo)-1)
                nick = '@' + recibido['from']['username']
                r = re.sub('____NICK____', nick, archivo[palabra])
                enviar('msg %s %s' % (recibido['to']['print_name'], r), p)
                # comunmente el bot va a escribir un mensaje nombrando a quien haya dicho alguna palabra clave
                # si hacemos funcionar la linea de abajo el bot "responderá" directamente al mensaje en el que lo nombran
                #enviar('reply %s %s' % (recibido['id'], r), p)
            
            # si el mensaje es solo '!sonando' el bot da cierta respuesta
            #elif recibido['text'] == '!sonando':
            # si el mensaje es solo '!sonando' y el nombre del grupo desde el que es enviado es 'RadioÑú', el bot responde, sino, no.
            elif recibido['text'] == '!sonando' and recibido['to']['print_name'] == 'RadioÑú':
                # url de la API
                req = urllib2.Request('http://www.radiognu.org/api?no_cover')
                response = urllib2.urlopen(req)
                html = response.read()
                datos = json.loads(html)
                # si no se ha solicitado una canción
                if cancion == '':
                    cancion = datos['title']
                # si la canción ya se ha solicitado
                elif cancion == datos['title']:
                    flood = True
                # si la canción es diferente a una solicitada anteriormente
                else:
                    cancion = datos['title']
                    flood = False
                
                # si la transmisión es en vivo y no es la misma canción que antes
                if datos['isLive'] and flood == False:
                    enviar('msg %s "🎤EN VIVO:\\n«%s» de %s\\n🎶 “%s”\\n👤 %s’"\n' % (conf['canal'], datos['show'], datos['broadcaster'], datos['title'], datos['artist']), p)
                # o si la transmisión no es en vivo y no es la misma canción que antes
                elif datos['isLive'] != True and flood == False:
                    enviar('msg %s "📻SONANDO EN DIFERIDO:\\n🎶 %s\\n👤 %s\\n💿 %s\\n📃 %s"\n' % (recibido['to']['print_name'], datos['title'], datos['artist'], datos['album'], datos['license']['shortname'] if datos["license"] != "" else ""), p)
