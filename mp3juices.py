#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
import httplib
import sys, htmllib, formatter, urllib, urllib2, os

from HTMLParser import HTMLParser
# from webrequest import artist

import logging
from execo import logger

logger.setLevel(logging.INFO)


#FYI Balise signalant une chanson
balise = '<span class="song_title">'
site="mp3juices.com"
class search(HTMLParser):
    
    def __init__(self,artist,title):
        HTMLParser.__init__(self)
        self.nb_results = 0
        self.current_counter = 0 #Indicate that a valid result is under process
        self.bitrate = 256 #Indicate the minimum bitrate to tolerate
        self.max_results = 1 #Maximum of results to download
        self.exclude_list = ["remix","mix","rmx"]
        self.data = "" # Contains the name of the song as found on the page
        self.naming = 'keep_original' # Set the naming policies of downloaded files
        self.artist = artist
        self.title = title
        self.files = []
        
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        for file in self.files:
            os.unlink(file)
    
    def download(self):
        self.nb_results = 0
        self.current_counter = 0 #Indicate that a valid result is under process
        self.bitrate = 256 #Indicate the minimum bitrate to tolerate
        self.max_results = 1 #Maximum of results to download
        self.exclude_list = ["remix","mix","rmx"]
        self.data = "" # Contains the name of the song as found on the page
        self.naming = 'keep_original' # Set the naming policies of downloaded files
        artist = self.artist
        title = self.title
        
        logger.info("Starting the "+site+" parser")
        logger.debug("Retrieving the song informations")
        logger.debug("ARTIST = %s",artist)
        logger.debug("TITLE = %s",title)
        song = artist+" - "+title
        request = song.replace(' ','-')
        
        song = song.lower()
        artist = artist.lower()
        title = title.lower()
        logger.info("SONG = "+song)
        logger.debug("REQUEST = "+request)
        
        logger.info("Performing the request...")
        conn = httplib.HTTPConnection(site)
        conn.request("GET", "/search/"+request)
        r1 = conn.getresponse()
        
        logger.debug("Server Answer = %r %r",r1.status,r1.reason)
        data1 = r1.read()
        logger.debug("Parsing the results page for results")
        parser = search(artist,title)
        parser.feed(data1)
        
        logger.debug("Closing the connexion")
        conn.close()
        
        #Nombre de résultats
        logger.info("Number of results = %r",parser.nb_results)
        return parser.nb_results
    
    def handle_starttag(self, tag, attrs):
        logger.debug("Encountered a start tag: %s",tag)
        if "input" in tag and self.current_counter > 0 and self.nb_results <= self.max_results:
            logger.debug("Encountered a start tag: %s",tag)        
            # ww8 / ww9 can be used to detect the downloading URL
            if "mp3juices.com/download/" in attrs[2][1] and "url" in attrs[1][1]:
                url = attrs[2][1]
                logger.debug("URL of the song")
                logger.debug(url)
                self.current_counter -= 1
                
                logger.debug("Protecting the address with double quotes")
                url = '"'+url+'"'
                os.system("wget "+url+" -O "+"XY")
                if 'keep_original' not in self.naming: # We make a choice between the original name of the file or the search terms
                    os.rename("XY",self.artist.title()+" - "+self.title.title()+".mp3")
                else:
                    os.rename("XY",self.data.title()+".mp3")
                
                return
            
        
    
    def handle_endtag(self, tag):
        return
        logger.debug("Encountered a end tag: %s",tag)
    
    def handle_data(self, data):
        data = data.lower()
        song = self.artist+" - "+self.title
        if song in data:
            for word in self.exclude_list:
                if word in data and word not in song:
                    logger.debug("Encountered some exclude term in the results. Skip it. (-%s- was found)",word)
                    return
            logger.debug("Encountered some data: %s",data)
            self.nb_results += 1
            self.current_counter += 1
            self.data = data
