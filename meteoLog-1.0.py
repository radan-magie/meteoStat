#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import requests
import collections
from time import strptime, mktime, strftime, localtime, sleep
from datetime import datetime
from BeautifulSoup import BeautifulSoup as BS
import csv
import os.path
#-------------------------------------------------------------------------------
# Todo:
# - funzione lettura dati
# - mostro a terminale per debug
# - generazione statistiche
# - generazione Grafico ( Pycairo )
# - mettere contatori: numero cicli, tempo lancio, durata.
#-------------------------------------------------------------------------------
class meteoLog:
    ''' Una classe per registrare i dati meteo. '''
    def __init__(self):
        # Inizializzazione attributi
        self.source_url = "http://www.ragnavela.it/meteo/index.htm"
        self.data_path = "./data/export.txt"
        self.lock_p = './locks/paused'
        self.lock_r = './locks/running'
        self.lock_s = './locks/stop'
        self.refr_secs = 60 #tempo di refresh
        self.status = None
        self.raw_data = None
        self.data = None
        self.go_on = True
        self.paused = False
        self.running = False
        self.pid = os.getpid()

#-------------------------------------------------------------------------------
# Sarebbe da scrivere nel file il pid del processo.
    def set_running(self): 
        print('PID: '+str(self.pid))
        self.touch(self.lock_r, self.pid)
        self.running = True

#-------------------------------------------------------------------------------
# Sarebbe da far tornare il pid del processo letto dal file di lock
    def is_running(self):
        self.running = os.path.isfile(self.lock_r)
        return self.running

#-------------------------------------------------------------------------------
    def not_running(self):
        os.remove(self.lock_r)
        self.running = False

#-------------------------------------------------------------------------------
    def can_go(self):
        self.go_on != os.path.isfile(self.lock_r)
        return self.go_on
        
#-------------------------------------------------------------------------------
    def is_paused(self):
        self.paused = os.path.isfile(self.lock_p)
        return self.paused

#-------------------------------------------------------------------------------
    def unpause(self):
        os.remove(self.lock_p)
        self.paused = False

#-------------------------------------------------------------------------------
    def touch(self, path, data=None):
        data = str(data)
        with open(path, 'w') as f:
            f.write(data)
            os.utime(path, None)

#-------------------------------------------------------------------------------
    def run_one(self):
        # print('Run lanciato')
        self.get_data()
        if self.raw_data :
            self.convert_data()
            self.write_data()
            self.status = 'OK'
        else :
            self.status = 'KO'

#-------------------------------------------------------------------------------
    def run_loop( self, wait=False ):
        if self.is_running():
            print( 'Already running' )
            exit(1)
        else :
            self.set_running()
            if not wait :
                wait = self.refr_secs # Intervallo di loop
            while self.can_go():
                print( 'Acquisizione dati...\n' )
                self.run_one()
                self.show_last()
                print( '\nPausa di '+ str(wait) +' secondi' )
                sleep( wait )
            self.not_running()

#-------------------------------------------------------------------------------
# Controllo se c'è il file di pausa
    def is_paused(self):
        self.paused = os.path.isfile(self.lock_p)
        return self.paused
        
#-------------------------------------------------------------------------------
# Formattare in modo decente x schermo. ( vedere vecchie versioni )
    def show_last(self):
        print self.data
        # Sarebbe da usare una tabella o incolonnare
#-------------------------------------------------------------------------------
# Scarica i dati ed imposta l'attributo self.raw_data
    def get_data(self):
        attempts = 0
        #print(source_url)
        while attempts < 3:
            try:
                #print( 'provo a fare una request' )
                html = requests.get( self.source_url ).content
                #print(html)
                soup = BS(html)
                tds = soup.findAll('td')# prendo dati all'interno di <td>
                td_data = []
                for td in tds:
                     inner_text = td.text
                     strings = inner_text.split("\n")
                     td_data.extend([string for string in strings if string]) # capire cosa fa.
                break
            except requests.exceptions.RequestException as e:
                attempts += 1
                print type(e)
                td_data = False
                break
        self.raw_data = td_data
#-------------------------------------------------------------------------------
# Conversione specifica per meteo ragnavela.
    def convert_data( self ):
        data = self.raw_data
        mesi = dict()
        mesi['gennaio'] = '01'
        mesi['febbraio'] = '02'
        mesi['marzo'] = '03'
        mesi['aprile'] = '04'
        mesi['maggio'] = '05'
        mesi['giugno'] = '06'
        mesi['luglio'] = '07'
        mesi['agosto'] = '08'
        mesi['settembre'] = '09'
        mesi['ottobre'] = '10'
        mesi['novembre'] = '11'
        mesi['dicembre'] = '12'
        read = dict()
        #read['e_time'] = strftime("%Y%m%d-%H:%M:%S", localtime() )
        #print( read['e_time'] )
        read['00_timestamp'] = mktime( localtime() )
        read['r_time'] = data[0].encode("ascii").split(" ")
        # Conversione in timestamp:
        read['r_timestamp'] = read['r_time'][4] + mesi[read['r_time'][3]] + read['r_time'][2] + '-' + read['r_time'][0] + ':00'
        read['01_r_time'] = read['r_timestamp']
        read['r_timestamp'] = strptime( read['r_timestamp'], "%Y%m%d-%H:%M:%S" )
        read['10_r_times'] = mktime(read['r_timestamp'])
        del read['r_time']
        del read['r_timestamp']
        read['20_temp'] = data[2].split(" ")[0].encode("ascii")
        read['30_press'] = data[4].split(" ")[0].encode("ascii")
        read['40_umid'] = data[6].split(" ")[0].encode("ascii")
        read['50_vent_max'] = (float)(data[8].split(" ")[0].encode("ascii"))*1.852 # convertito in km/h
        read['60_vent_med'] = (float)(data[10].split(" ")[0].encode("ascii"))*1.852 # convertito in km/h
        read['70_vent_grad'] = data[12].split(" ")[0][:-1].encode("ascii")
        read['71_vent_dir'] = data[12].split(" ")[1].encode("ascii")
        read['80_vent_bea_1'] = data[13].split("&nbsp;")[1].encode("ascii") # togliere la F
        read['81_vent_bea_2'] = data[14].encode("ascii")
        self.data = collections.OrderedDict(sorted(read.items()))
#-------------------------------------------------------------------------------
    def write_data( self ):
        d_str = ''
        # in alternativa si poteva usare :
        # ' '.join(['word1', 'word2', 'word3'])
        for d in self.data:
            d_str += str(self.data[d])+'\t'
        d_str = d_str[:-1]
        try:
            f = open( self.data_path , 'a' )
            f.write( d_str+'\n' )
            f.close()
            return True
        except Exception, ex:
            print( ex )
            return False

#-------------------------------------------------------------------------------
    def read_data():
        self.data_path
        f = open(data_path, r )
        d_read = f.readlines()
        f.close()
        return d_read
#-------------------------------------------------------------------------------
# TODO: funzione di decodifica dati
    def decode_data():
        pass
#===============================================================================
'''
    Script di avvio,
    valutare se trasformare in thread.
'''
if __name__ == "__main__":
    description = '''Params: start|test|stats|stop
    start: \t Infinite loop
    test: \t Run once
    stats: \t Show stats
    stop: \t Soft stop infinite loop after a cycle ( run in a new prompt)'''
    if ( len(sys.argv) > 1 ):
        action = sys.argv[1]
    else:
        action = 'Not given'
    ml = meteoLog()
    print('Options: "'+action+'"')
    if action == 'start': # Ciclo infinito
        print('Meteolog starts!\nRun in a new prompt with parameter "stop" to quit or press CTRL+C')
        ml.run_loop()
    elif action == 'test': # Solo una volta
        print('Meteolog test')
        ml.run_one()
        ml.show_last()
    elif action == 'stats': # Da rifinire.
        print('Meteolog statistics')
        ml.status()
    elif action == 'stop':
        print('Meteolog stops.')
        ml.not_running()
    elif action == 'help' or  action == '-h' :
        print(description)
    else: # Mostro help con parametri
        print(description)
#===============================================================================
