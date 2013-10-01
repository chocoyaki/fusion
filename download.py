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

import logging
from execo import logger

logger.setLevel(logging.INFO)

import mp3juices

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

class xmldownload():
    
    def __init__(self,target_folder = "./"):
        return

source_folder = os.getcwd()
print len(sys.argv)

if len(sys.argv) > 1:
    script, target_folder = argv
else: 
    target_folder = "."
os.chdir(target_folder)
logger.info("Targer Folder = %s",os.getcwd())
logger.info("Looking for XML files...")
cpt_files = 0
for item in os.listdir(target_folder):
    if item.endswith(".xml"):
        
        xml_file = item
        tree = ET.parse(item)
        root = tree.getroot()
        genre = item.split(".")[0]
        destination_folder = "./"+genre
        try:
            os.mkdir(destination_folder)
        except OSError:
            logger.info("The folder %s already exists",destination_folder)
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
                    dl = mp3juices.search(artist,titre,destination_folder)
                    logger.info("destination_folder = %s",destination_folder)
                    nb_res = dl.download()
                    if nb_res > 0:
                        logger.info("Win!")
                        setAsDownloaded(child)
                        dl_cpt +=1
                    else:
                        logger.info("Loss!")
                    total+=1        
logger.info("[%s] %d / %d new songs were found and downloaded!",genre,dl_cpt,total)
logger.info("%d valid XML files!",cpt_files)

tree.write(xml_file)        


os.chdir(source_folder)
#We got back to the folder of the script


# Pour chaque fichier xml du dossier (si pas de dossier en entrée, chercher dans le dossier courant"
# Vérifier si le fichier a été téléchargé auparavant
# Récupérer titre et artiste
# Lancer une requête sur mp3juices
# Editer le fichier si le téléchargement a été effectué
# Statistiques : nombre de chansons téléchargées/total liste