# Selenium Practice

## Setup

```shell
git clone git@github.com:matthewDavidson1997/Selenium-Practice.git
cd Selenium-Practice
mamba env create -f environment.yml
conda activate selenium
```

In a linux (perhaps WSL2) environment, you may need to install chrome.

```shell
sudo apt update
sudo apt upgrade
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

## Running

```shell
python selenium_scraper.py
```
