#!/usr/bin/env python

import csv
import re
import os
import sys
import time
import urllib
import progressbar
import requests
import queue

scriptdir = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(scriptdir)

outputdir = "pdf_downloads"
search_criteria = "+datasheet+pdf"
input_file = "{}/input.csv".format(scriptdir)

import splinter
from splinter import Browser

if __name__ == "__main__":
    if not os.path.isfile(input_file):
        print("* File '{}' doesn't exists".format(input_file))
        sys.exit()

    print("* Running chromedriver...")
    browser = Browser('chrome')

def main():
    with open(input_file, 'rt', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for idx, row in enumerate(reader):
            process_row(idx, remove_non_ascii("".join(row)))

def remove_non_ascii(input):
    nonascii = "".join(i for i in input if ord(i) < 128)
    nonascii = re.sub('[:.,()]', '', nonascii)
    nonascii = re.sub(' +', ' ', nonascii).strip()
    return nonascii

def process_row(idx, string):
    if string == "":
        return

    print("* Looking for '{}'...".format(string))
    browser.visit('https://duckduckgo.com/?q={}{}'.format(string, search_criteria))
    try:
        # Google selector
        #     find_by_xpath("//span[text()='[PDF]']/following-sibling::a").first

        # DuckDuckGo selector
        first_pdf = browser.find_by_xpath("//span[text()='PDF']/parent::a").first
        print("* Found PDF! {}".format(first_pdf.text))
        print("* URL: {}".format(first_pdf['href']))

        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        pdf_out = '{}/{:02}. {} @ {}.pdf'.format(outputdir, idx, string, first_pdf.text)
        print("* Saving to '{}'...".format(pdf_out))
        download_file(first_pdf['href'], pdf_out)
    except:
        print("* Error: {}".format(sys.exc_info()[0]))
        pass

def download_file(url, out):
    if os.path.isfile(out):
        print("* File '{}' already exists".format(out))
        return

    local_filename = out
    r = requests.get(url, stream=True)
    f = open(local_filename, 'wb')
    file_size = int(r.headers['Content-Length'])

    if file_size > (30 * 1024 * 1024):
        print("* File '{}' is too big!".format(file_size))
        return

    chunk = 1
    num_bars = file_size / chunk
    bar =  progressbar.ProgressBar(maxval=num_bars).start()
    i = 0

    for chunk in r.iter_content():
        f.write(chunk)
        bar.update(i)
        i += 1

    f.close()
    return

if __name__ == "__main__":
    main()
    browser.quit()
