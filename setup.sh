# Python+package installation

sudo apt-get update
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

sudo apt install gcc -y
sudo apt install python -y
sudo apt install python3.9 -y
sudo apt-get install libmysqlclient-dev -y
sudo apt-get install python-dev -y
sudo apt-get install python3.9-dev -y
sudo apt-get install python3-pip -y
sudo apt install libffi-dev -y

sudo apt-get install libxml2-dev libxslt1-dev
sudo apt-get install libblas-dev  liblapack-dev
sudo apt-get install python3.9-distutils -y

# pip installation
#wget https://bootstrap.pypa.io/get-pip.py
#sudo python get-pip.py
sudo apt install nginx -y
#sudo pip install gunicorn==19.7.1
#sudo pip install virtualenv
sudo apt-get install python3-virtualenv -y

# PostgrelSQL
sudo apt-get update
sudo apt-get install python-pip libpq-dev postgresql postgresql-contrib -y
sudo apt install libcurl4-openssl-dev libssl-dev -y
sudo apt-get install swig -y
sudo apt-get install libpulse-dev -y

# Install Java JDK
sudo apt install openjdk-11-jdk -y

# Install PHP7.2
sudo apt install software-properties-common
sudo add-apt-repository ppa:ondrej/php
sudo apt update
sudo apt install php7.2-cli

# Install unzip
sudo apt install unzip -y


# Install zip
sudo apt install zip -y

# Install Certbot
#sudo apt-get update
#sudo apt-get install software-properties-common
#sudo add-apt-repository universe
#sudo add-apt-repository ppa:certbot/certbot
#sudo apt-get update
#sudo apt-get install certbot python-certbot-nginx

# SSO SAML Auth package

sudo apt-get install xmlsec1 -y

# Install Supervisor service

sudo apt-get install supervisor -y

sudo apt update

sudo apt install redis-server -y

sudo apt-get install wkhtmltopdf -y
sudo apt-get install xvfb -y


# Install ffmeg for CognoMeet Merging

sudo apt install ffmpeg -y

# Install node js

sudo apt install nodejs -y

# conversion 
sudo apt-get install libenchant1c2a

# Install Chromium Driver for Advance FAQ Extraction using Selenium

sudo apt-get install chromium-chromedriver

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
sudo apt-get install xmlsec1

# Install wkhtmltopdf version=0.12.5  

wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
sudo dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb
sudo apt install -f

# To Install Font(This supports only indian languages)  

sudo apt-get install fonts-indic
