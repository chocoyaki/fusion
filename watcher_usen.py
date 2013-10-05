#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
import httplib
import sys, htmllib, formatter, urllib, urllib2, os

from HTMLParser import HTMLParser

from contextlib import closing
from selenium.webdriver import Firefox # pip install selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import re
import unicodedata
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement
from xml.dom import minidom
import datetime

import os
import re
import time
import sys
import thread

from threading import Thread, BoundedSemaphore

class thread_usen(Thread):
    def __init__ (self,param):
        
        Thread.__init__(self)
        self.protocol="http://"
        self.site="music.usen.com" # Domain only
        self.page="/nowplay/sound-planet/" #Page only
        self.genre = param
        self.parser = UsenParser(self.genre)
        self.band = self.parser.get_band(self.genre)
        self.number = self.parser.get_channel(self.genre)
        self.request = '?band='+self.band+'&chno='+self.number
        self.url = self.protocol+self.site+self.page+self.request
        
    def run(self):
        
        pool_sema.acquire()
        
        parser = self.parser
        
        with closing(Firefox()) as browser:
            browser.get(self.url)
            w = WebDriverWait(browser, 10)
            w.until(lambda driver: driver.find_element_by_class_name("np03")) # Wait until the javascript is loaded
            page_source = browser.page_source
            parser.feed(page_source)
            parser.write()
        
        print "["+self.genre+"] New songs = "+str(parser.new_entries)
        
        pool_sema.release()
        
        
# doc = http://element34.ca/blog/webdriverwait-and-python


## This script is in charge of periodically check USEN lists and save the information in a xml file
## Songs information = artist / title / genre / date d'ajout / nombre d'essais
## Retrieve statistics = date / songs added / new songs

## {{{ http://code.activestate.com/recipes/466341/ (r1)

def generated_on():
    return str(datetime.datetime.now())

def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('unicode_escape')


# ------------------------------------------------------------------------
# Sample code below to illustrate their usage

def write_unicode_to_file(filename, unicode_text):
    """
    Write unicode_text to filename in UTF-8 encoding.
    Parameter is expected to be unicode. But it will also tolerate byte string.
    """
    fp = file(filename,'wb')
    # workaround problem if caller gives byte string instead
    unicode_text = safe_unicode(unicode_text)
    utf8_text = unicode_text.encode('utf-8')
    fp.write(utf8_text)
    fp.close()
## end of http://code.activestate.com/recipes/466341/ }}}


def convert(s):
        """ Decode a 'japanese' string of char to a ready-to-work string """
        try:
            return s.group(0).encode('latin1').decode('utf8')
        except:
            return s.group(0)
        
class UsenChannels:
    """ Define the channels to check at each execution """
    def __init__(self):
        self.channel_list = {}
        self.channel_list["jazzy_hip_hop"] = ["D","63"]
        self.channel_list["rock_and_pops"] = ["A","39"]
        self.channel_list["black_music"] = ["A","40"]
        self.channel_list["R_and_B"] = ["B","15"]
        self.channel_list["hip_hop"] = ["B","16"]
        self.channel_list["soul"] = ["B","17"]
            
        self.channel_list["reggae"] = ["B","29"]
        self.channel_list["R_and_B_classics"] = ["B","53"]
        self.channel_list["popular_hits_now"] = ["B","30"]
        self.channel_list["funky_beats"] = ["D","09"]
        self.channel_list["slow_jazz"] = ["H","11"]
        self.channel_list["bossa_nova"] = ["D","30"]
        self.channel_list["funk"] = ["D","45"]
        self.channel_list["bar_time_popular"] = ["I","16"]
        self.channel_list["fitness_popular"] = ["I","17"]
        self.channel_list["hits_90"] = ["B","28"]

class UsenParser(HTMLParser):
    """ Defines the functions required to launch and retrive the content of a UsenMusic page
    The results are saved in a xml file"""
    
    balise = '<li class="np03">'
    # The information about the song is after that tag
    # Pattern = Title / Song
    
    def __init__ (self,genre, channels = UsenChannels()):
        HTMLParser.__init__(self)
        #self.page = page
        self.website = "Usen Music"
        self.recording = 0
        self.data = []
        self.genre = genre
        self.file = genre+".xml"
        self.new_entries = 0
        
        self.channel_list = channels
        
        filename = self.file
        new_content = "<"+genre+">"+"</"+genre+">"
        try:
            with open(filename):
                print "filename = "+filename
                self.tree = ET.parse(self.file)
                self.song_list = self.tree.getroot()
        except IOError:
            print "Oh dear. "+filename+" doesn't exist. A new file will be created",filename
            new_file = open(filename,"w")
            new_file.write(new_content)
            new_file.close()
                        
            self.tree = ET.parse(self.file)
            self.song_list = self.tree.getroot()
            
        index = 0
        root = self.song_list
        self.songs_from_xml = [] #Used to put the xml in memory to avoid duplicate entries
        
        for child in root:
            artist = root[index][0].text
            title = root[index][1].text
            
            entry = title+" / "+artist
            self.songs_from_xml.append(entry) # title / artist
            #print entry
            #print self.songs_from_xml
            
            #print self.dict_songs.get(title)
            index += 1
   
         
    def get_band(self,genre):
        return self.channel_list.channel_list[genre][0]
            
    def get_channel(self,genre):
        return self.channel_list.channel_list[genre][1]
        
        
    def write(self):
        self.tree.write(self.genre+".xml")
    
#     def __init__ (self,tree):
#         HTMLParser.__init__(self)
#         #self.page = page
#         self.recording = 0
#         self.data = []
#         self.tree = tree
#         
    def handle_starttag(self, tag, attrs):
        if tag != 'li':
            return
        
        if self.recording:
            self.recording += 1
            return
        
        for name,value in attrs:
            if name == 'class' and value == 'np03':
                self.recording = 1 # We indicate to record the data matching those conditions
                break
            else:
                return
        
        
    def handle_endtag(self, tag):
        if tag == 'li' and self.recording:
            self.recording -= 1
         
            #print self.data

    def prettify(self,elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    
    def exotic_to_str(self,base_data):
        table = dict([(x + 0xFF00 - 0x20, unichr(x)) for x in xrange(0x21, 0x7F)] + [(0x3000, unichr(0x20))])
        clean_data =  base_data.translate(table)
        return clean_data
    
    def get_title(self,string):
        table = string.split(" / ")
        return table[0]
    
    def get_artist(self,string):
        table = string.split(" / ")
        return table[1]
    
    def save_song(self,song_data):
        
        # If not present
        # Dictionnaire Géant avec artist / title?
        # Si présent dans le dico, alors on ne rajoute pas
        
        # Ajouter des statistiques
        
        properties = {'CreationDate' : generated_on()
                      ,'From' : self.website
                      ,'Downloaded' : 'no'
                      }
        
             
        song = ET.SubElement(self.song_list,'song',properties)
        
        artist = ET.SubElement(song, 'artist')
        artist.text = self.get_artist(song_data)
        title = ET.SubElement(song, 'title')
        title.text = self.get_title(song_data)
        dl_link = ET.SubElement(song, 'WebLink')
        dl_link.text = "null"
        
        return song
        
    def handle_data(self, data):
        if self.recording:
            song = self.exotic_to_str(data)
            self.data.append(song)
            #print song
            if song not in self.songs_from_xml: #if the song was not saved before
                self.save_song(song)
                self.new_entries += 1
            

#http://music.usen.com/nowplay/sound-planet/?band=D&chno=63
url_dev = "file:///home/dbalouek/dev/mp3fusion/JAZZY%20HIP%20HOP%20NOW%20PLAYING%20|%20USEN%EF%BC%88%E6%9C%89%E7%B7%9A%EF%BC%89%E9%9F%B3%E6%A5%BD%E6%94%BE%E9%80%81%20%E7%95%AA%E7%B5%84%E6%A1%88%E5%86%85%20|%20music.usen.com.html"

protocol="http://"
site="music.usen.com" # Domain only
page="/nowplay/sound-planet/" #Page only

channels = UsenChannels()
cpt_genre = 1

threads = []
maxconnections = 4
pool_sema = BoundedSemaphore(value=maxconnections)

for genre in channels.channel_list:
    current = thread_usen(genre)
    threads.append(current)
    current.start()

for t in threads:   
    t.join(60.0)
    #print t.genre+" is done!"
    
    #print parser.data
    #print parser.prettify(parser.song_list)

#Ecrire une boucle de parsage vers mp3juices/mp3.li puis passer downloaded à yes
# Boucles sur tous les genres
     
# conn.close()
        
    
    