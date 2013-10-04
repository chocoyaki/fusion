#!/bin/bash

install:
	sudo apt-get install python-pip firefox -y
	sudo pip install selenium
	mkdir -p ~/src/
	cd ~/src/
	git clone git://scm.gforge.inria.fr/execo/execo.git
	cd execo/
	make install PREFIX=$HOME/.local
	PYTHONHOMEPATH="$HOME/.local/"$(python -c "import sys,os; print os.sep.join(['lib', 'python' + sys.version[:3], 'site-packages'])")
	export PYTHONPATH="$PYTHONHOMEPATH${PYTHONPATH:+:${PYTHONPATH}}"
	cd ~/Dropbox/software_files_linux/
	git clone git@github.com:chocoyaki/fusion.git

update:
	git --git-dir="/home/dbalouek/Dropbox/software_files_linux/fusion/.git" pull

start:
	cd ~/Dropbox/software_files_linux/fusion/
	~/Dropbox/software_files_linux/fusion/watchdog.py "/home/dbalouek/Dropbox/software_files_linux/fusion/"
	ssh chocoyaki@kimchoco "cd ~/Dropbox/software_files_linux/fusion/; ./download.py"
	date +"%m-%d-%Y %T" >> ~/Dropbox/software_files_linux/fusion/history.log