#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import collections
from time import strptime, mktime, strftime, localtime, sleep
from datetime import datetime
from BeautifulSoup import BeautifulSoup as BS
import csv
#-------------------------------------------------------------------------------
# funzione lettura dati
# mostro a terminale per debug
# generazione statistiche
# generazione Grafico
# mettere contatori: numero cicli, tempo lancio, durata.
#-------------------------------------------------------------------------------
class meteoLog:
   ''' Una classe per registrare i dati meteo. '''
   def __init__(self):
      # Inizializzazione attributi
      self.source_url = "http://www.ragnavela.it/meteo/index.htm"
      self.data_path = "./data/export.txt"
      self.refr_secs = 60 #tempo di refresh
      self.status = None
      self.raw_data = None
      self.data = None
      self.go_on = True
      self.paused = False
      self.pauseBtn = 'p' # tassto di pausa
      self.stopBtn = 'q' # tasto di stop
      self.statBtn = 's' # tasto statistiche

#-------------------------------------------------------------------------------
   def run_one(self):
      print('Run lanciato')
      self.get_data()
      if self.raw_data :
         self.convert_data()
         self.write_data()
         self.status = 'OK'
      else :
         self.status = 'KO'
   #exit()

#-------------------------------------------------------------------------------
   def run_loop(self, wait=False):
      if not wait :
         wait = self.refr_secs # Intervallo di loop
      while self.go_on:
         self.is_paused()
         if self.paused :
            print('.')
            sleep( 10 )
            break
         print( 'Acquisizione dati...\n' )
         self.run()
         self.show_last()
         self.canGo()
         if self.go_on :
            print( 'Pausa di '+ str(wait) +' secondi' )
            sleep( wait )
         else :
            print('\n--- FINE ---\n')
            break
      #exit()

#-------------------------------------------------------------------------------
# TODO: funzione di controllo Stop, abbozzata,
# devo controllare se è stato premuto un tasto per fermarmi.
   def can_go(self):
      # es. sys.keypress == stopBtn
      check = False
      self.go_on = check

#-------------------------------------------------------------------------------
# TODO: funzione di controllo Pausa, abbozzata,
# devo controllare se è stato premuto un tasto per andare in pausa. <-- vedere come si fa self.pauseBtn
   def is_paused(self):
      # es. sys.keypress == self.pauseBtn
      check = False
      self.paused = check

#-------------------------------------------------------------------------------
# Formattare in modo decente x schermo. ( vedere vecchie versioni )
   def show_last(self):
      print self.data
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
      read['0_timestamp'] = mktime( localtime() )
      read['r_time'] = data[0].encode("ascii").split(" ")
      # Conversione in timestamp:
      read['r_timestamp'] = read['r_time'][4] + mesi[read['r_time'][3]] + read['r_time'][2] + '-' + read['r_time'][0] + ':00'
      read['r_timestamp'] = strptime( read['r_timestamp'], "%Y%m%d-%H:%M:%S" )
      read['10_r_time'] = mktime(read['r_timestamp'])
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
         d_str += str(in_data[d])+'\t'
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

if __name__ == "__main__":
   print('OK')
   ml = meteoLog()
   ml.run_one()
   #ml.loop()
   print ml.status



