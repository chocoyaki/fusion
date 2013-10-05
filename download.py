#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
import httplib
import sys, htmllib, formatter, urllib, urllib2, os

from HTMLParser import HTMLParser
# from webrequest import artist

from contextlib import closing
import re
import unicodedata
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement
from xml.dom import minidom
import datetime
from time import sleep

import sys
import logging
from execo import logger
import socket

logger.setLevel(logging.INFO)

import mp3juices

def strip_accents(s):
    s = s.decode('unicode-escape')
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
   
# create a subclass and override the handler methods
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

def hasBeenDownloaded(element):
    if element.attrib["Downloaded"] == "no":
        return False
    else:
        return True
    
def setAsDownloaded(element):
    element.attrib["Downloaded"] = "yes"
    return hasBeenDownloaded(element)

def replacements(string):
        string.replace("&","and")
        s = strip_accents(string)
        return s

class xmldownload():
    
    def __init__(self,xml_folder = "./"):
        return

source_folder = os.getcwd()
print len(sys.argv)

if len(sys.argv) > 1:
    script, xml_folder, fusion_folder = argv
else: 
    xml_folder = "."
    fusion_folder = "/home/ftp/Musique/fusion/"
os.chdir(xml_folder)
logger.info("Targer Folder = %s",os.getcwd())
logger.info("Looking for XML files...")
cpt_files = 0
for item in os.listdir(xml_folder):
    if item.endswith(".xml"):
        
        xml_file = item
        tree = ET.parse(item)
        root = tree.getroot()
        genre = item.split(".")[0]
        xml_folder = fusion_folder+"/"+genre
        try:
            os.mkdir(xml_folder)
        except OSError:
            logger.info("The folder %s already exists",xml_folder)
        if root.tag == genre:
            logger.debug("%s.xml is a valid file!",genre)
            cpt_files +=1
            dl_cpt=0
            total=0
            for child in root:
                child_cpt = 0
                if hasBeenDownloaded(child) == False:
                    artist = safe_unicode(child[0].text).encode('utf-8')
                    titre = safe_unicode(child[1].text).encode('utf-8')
                    
                    replacements(artist)
                    replacements(titre)
                    logger.info("Song to download: %s - %s",artist,titre)
                    dl = mp3juices.search(artist,titre,xml_folder)
                    logger.info("xml_folder = %s",xml_folder)
                    
                    #Management of timeout and socket errors
                    try:
                        nb_res = dl.download()
                    except socket.error as msg:
                        nb_res = -1
                        continue
                    except KeyboardInterrupt:
                        nb_res = -1
                        raise
                    if nb_res > 0:
                        logger.info("Win!")
                        setAsDownloaded(child)
                        logger.info("Song has been tag download as : %s / %s - %s",hasBeenDownloaded(child),artist,titre)
                        dl_cpt +=1                     
                    else:
                        logger.info("Loss!")
                    total+=1
            tree.write(xml_file)  
logger.info("[%s] %d / %d new songs were found and downloaded!",genre,dl_cpt,total)
logger.info("%d valid XML files!",cpt_files)

        


os.chdir(source_folder)
#We got back to the folder of the script


# Pour chaque fichier xml du dossier (si pas de dossier en entrée, chercher dans le dossier courant"
# Vérifier si le fichier a été téléchargé auparavant
# Récupérer titre et artiste
# Lancer une requête sur mp3juices
# Editer le fichier si le téléchargement a été effectué
# Statistiques : nombre de chansons téléchargées/total liste