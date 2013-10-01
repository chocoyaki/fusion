#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
import httplib
import sys, htmllib, formatter, urllib, urllib2, os

from HTMLParser import HTMLParser
# from webrequest import artist

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

import logging
from execo import logger

logger.setLevel(logging.INFO)

import mp3juices

# create a subclass and override the handler methods
def hasBeenDownloaded(element):
    if child.attrib["Downloaded"] == "no":
        return False
    else:
        return True

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
        tree = ET.parse(item)
        root = tree.getroot()
        genre = item.split(".")[0]
        if root.tag == genre:
            logger.debug("%s.xml is a valid file!",genre)
            cpt_files +=1
logger.info("%d valid XML files!",cpt_files)
for child in root:
    child_cpt = 0
    if hasBeenDownloaded(child) == False:
        artist = child[0].text
        titre = child[1].text
        logger.info("Song to download: %s - %s",artist,titre)
        dl = mp3juices.search(artist,titre)
        nb_res = dl.download()
        if nb_res > 0:
            logger.info("Win!")
        else:
            logger.info("Loss!")
    
os.chdir(source_folder)
#We got back to the folder of the script


# Pour chaque fichier xml du dossier (si pas de dossier en entrée, chercher dans le dossier courant"
# Vérifier si le fichier a été téléchargé auparavant
# Récupérer titre et artiste
# Lancer une requête sur mp3juices
# Editer le fichier si le téléchargement a été effectué
# Statistiques : nombre de chansons téléchargées/total liste