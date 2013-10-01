#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
import httplib
import sys, htmllib, formatter, urllib, urllib2, os

from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class mp3LiParser(HTMLParser):
	
	balise = '<div class="song_title">'
	
	def __init__(self,artist,title):
		HTMLParser.__init__(self)
		self.nb_results = 0
		self.artist = artist
		self.title = title
		
	
#    def handle_starttag(self, tag, attrs):
#        print "Encountered a start tag:", tag
#    def handle_endtag(self, tag):
#        print "Encountered an end tag :", tag
#    def handle_data(self, data):
#        print "Encountered some data  :", data
	def handle_starttag(self, tag, attrs):
		if tag != 'a':
			return
		
		i = 0
		
		for name, value in attrs:
			if name == 'class' and value == 'dl_link':
				my_dict = {}
				
				for i in range(0,4):
					my_dict[attrs[i][0]] = attrs[i][1]
					
				found = my_dict['title'].lower()
				match = "download "+artist+" - "+title+".mp3"
#				print "--------------"
#				print found
#				print match
#				print "--------------"
				
				if cmp(found, match ) == 0:
					self.nb_results+=1
					if self.nb_results == 1:
						print found
						print my_dict['href']
						full_link = "http://dl3.mp3.li/api/mp3li/local.audio.download/15MLNNJTQHNNV9MUCQFS4NR8LDN86KT6BR8QPBT1HPSBF918GMCH/Brother%20Ali%20-%20Uncle%20Sam%20Goddamn.mp3"
						filename = artist.title()+" - "+title.title()+".mp3"
						
						os.system("wget "+ my_dict["href"]+" -O "+"XY")
						os.rename("XY",filename)
						#, artist+" - "+title+".mp3")
				
			else: 
				return
		
#Recuperer les infos en arguments
script, artist, title = argv
song =  artist+"+-+"+title
song = song.replace(' ','+')
song = song.lower()
artist = artist.lower()
title = title.lower()
#song = "eminem - kim"
print "Song request : %s"% song

#Soumettre une requete web
# Définir un objet Site = nom/index/Plugin downloader
# Tester le code index avant de coninuer

site="mp3.li"
conn = httplib.HTTPConnection(site)
#conn.request("GET", "/index.php")
#r1 = conn.getresponse()
#print r1.status, r1.reason
#data1 = r1.read()

request= "?q="+song
conn.request("GET", "/index.php"+request)
r1 = conn.getresponse()
print r1.status, r1.reason
data1 = r1.read()
#print data1
parser = mp3LiParser(artist,title)
parser.feed(data1)
#Parser la page de résultat
#
#Une fois dans la section adéquate, chercher le tag ouvrant song_title; vérifier la correspondance artiste / titre;  si OK, lancer le téléchargement

# Identifier les résultats voulus (titre - artist = match avec requête)

# Récupérer le lien de téléchargement

#Lancer un download sur un lien

#Fermer la connexion
conn.close()

#Nombre de résultats
print "le nombre de résultats : %s"% parser.nb_results