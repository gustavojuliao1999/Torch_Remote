#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

# html requests
import requests
# htmldate
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
# nonce
import time
from itertools import count
# hmac
import hmac
import hashlib
# basee64 conversions
import base64
# json
import json
import mysql.connector
#pip install mysql-connector-python
# argparsepip
import argparse

NONCE_COUNTER = count(int(time.time() * 1000))


class pyvrageremoteAPI(object):
    """Classe por obter uma resposta do vrageremote"""

    def __get_htmldate(self):
        """Obtem data / hora atual em formato de data HTML (RFC1123)"""
        now = datetime.now()
        stamp = mktime(now.timetuple())
        return format_date_time(stamp)  # --> Wed, 22 Oct 2008 10:52:40 GMT

    def __get_nonce(self):
        """Pega a unique nonce"""
        return str(next(NONCE_COUNTER))

    def __build_message(self, method_url, nonce, htmldate):
        """Cria a mensagem a ser enviada ao servidor"""
        return method_url + "\r\n" + nonce + "\r\n" + htmldate + "\r\n"

    def __build_hash(self, message):
        """Calcula o hash da mensagem a ser enviada"""
        key_decoded = base64.b64decode(self.key)
        signature = hmac.new(key_decoded, message.encode('utf-8'),
                             hashlib.sha1)
        return base64.b64encode(signature.digest()).decode()

    def __build_request(self, resource):
        """Crie uma solicitação personalizada de acordo com as especificações da vrageremote"""
        method_url = self.remote_url + resource
        full_url = self.url + method_url
        print("Full URL:"+str(full_url))
        nonce = self.__get_nonce()
        htmldate = self.__get_htmldate()

        message = self.__build_message(method_url, nonce, htmldate)
        hmac_hash = self.__build_hash(message)

        headers = {'Date': '',
                   'Authorization': ''}
        headers['Date'] = htmldate
        headers['Authorization'] = nonce + ":" + hmac_hash

        request = requests.Request('GET', full_url, headers=headers)
        return request

    def get_resource_by_name(self, resource):
        """Retorna dados do vrageremote, por exemplo 'server', retorna dados em JSON"""
        request = self.__build_request(resource)
        prepped_request = request.prepare()

        with requests.Session() as session:
            response = session.send(prepped_request)
            json_data = json.loads(response.text)
            print(json_data)
            return json_data

    def get_resource_server(self):
        """Retorna informações do 'server'"""
        return self.get_resource_by_name('server')
    def get_server_all(self):
        """Retorna Todas as informações do server"""
        valjson = self.get_resource_by_name("server")
        #json_object = json.loads(valjson)
        data = (valjson["data"])
        q_players, ss, SimCpuLoad , UsedPcu , version = data["Players"], data["SimSpeed"], data["SimulationCpuLoad"], data["UsedPCU"], data["Version"]
        print("Players:",q_players," SS:", ss," SimCpuLoad:",SimCpuLoad," UsedPCU:",UsedPcu," Version:",version)
        return (q_players, ss, SimCpuLoad , UsedPcu , version)

    def get_session_players(self):
        """Retorna Todos os Players no server"""
        valjson = self.get_resource_by_name("session/players")
        data = (valjson["data"])
        players = (data["Players"])
        val_players = []
        for x in players:
            player = x
            #print(player)
            SteamID, PlayerName, Faccao, TagFacccao, Ping = player["SteamID"], player["DisplayName"], player["FactionName"], player["FactionTag"], player["Ping"]
           # print("Player"+str(x))
            val_players.append([SteamID, PlayerName, Faccao, TagFacccao, Ping])

        print(val_players)
        return val_players


    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.remote_url = "/vrageremote/v1/"


class db():


    mydb = mysql.connector.connect(
        host="",
        user="",
        password="",
        database=""
    )
    mycursor = mydb.cursor()

    def datahora(self):
        data_e_hora_atuais = datetime.now()
        data_e_hora_em_texto = data_e_hora_atuais.strftime('%Y-%m-%d %H:%M:%S')
        print(data_e_hora_em_texto)
        return data_e_hora_em_texto

    def server(self, server_all):
        players, ss, SimCpuLoad, UsedPcu, version = server_all
        data_e_hora_atuais = datetime.now()
        data_e_hora_em_texto = data_e_hora_atuais.strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO status_serverino (players, ss, SimCpuLoad, UsedPcu, versao, datatime) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (players, ss, SimCpuLoad , UsedPcu , version,data_e_hora_em_texto )
        self.mycursor.execute(sql, val)
        self.mydb.commit()
        return self.mycursor.fetchone()

    def players(self, all_players):
        data_e_hora_atuais = datetime.now()
        data_e_hora_em_texto = data_e_hora_atuais.strftime('%Y-%m-%d %H:%M:%S')
        for x in all_players:
            sql = "INSERT INTO status_players (SteamID, PlayerName, Faccao, TagFacccao, Ping, datatime) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (str(x[0]), x[1], x[2], x[3], str(x[4]),data_e_hora_em_texto)
            self.mycursor.execute(sql, val)
            print("Add Player",val)
            print(data_e_hora_em_texto)

        self.mydb.commit()
        return self.mycursor.fetchone()



if __name__ == '__main__':
    #VrageRemote
    url = ""
    key = ""
    api = pyvrageremoteAPI(url, key)

    db = db()

    print("--------------------------")
    while True:
        #test = input()
        try:
            db.server(api.get_server_all())
            db.players(api.get_session_players())
            print("--------------------------------------------------------------------------------------------------------------")
            time.sleep(60)
        except:
            print("Erro")

    # db.server(api.get_server_all())
    # db.players(api.get_session_players())

    # VrageRemote Serverino

    # print(api.get_server_all())
    #valjson = api.get_resource_by_name("server")
    #json_object = json.loads(valjson)
    #data = (valjson["data"])
    #print("Players:"+str(data["Players"]))
