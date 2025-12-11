#!/usr/bin/env python3
# -*- coding: utf8 -*-
#-------------------------------------------------------------------------------
# Name:        get xml and converto to json
# Purpose:     publish to grafana/influx
#
# depends on:
#   WOSPi by Torkel M. Jodalen <tmj@bitwrap.no>
#   http://www.annoyingdesigns.com  -  http://www.bitwrap.no
#
# Author:      Peter Lidauer <plix1014@gmail.com>
#
# Created:     21.07.2024
# Copyright:   (c) Peter Lidauer 2024
# Licence:     CC BY-NC-SA http://creativecommons.org/licenses/by-nc-sa/4.0/
#-------------------------------------------------------------------------------
# Changes:
#

import sys,os
import json
import urllib.request, urllib.error, urllib.parse
import re
import requests
import xml.etree.ElementTree as ET


from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
from math import modf

# request user agent string
headers_agent  = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'}

# read url and country from environment
WXDATA_URL        = os.environ.get('WXDATA_URL')
WXSTATION_COUNTRY = os.environ.get('WXSTATION_COUNTRY')


if WXDATA_URL != None:
    wxurl = WXDATA_URL
else:
    # fallback url if env variable not set
    wxurl = 'http://www.lidauer.net/wetter'

if WXSTATION_COUNTRY != None:
    tag_country = WXSTATION_COUNTRY
else:
    # fallback country if env variable not set
    tag_country = 'AT'


# build full url
wxfile = wxurl + '/' + 'wxdata.xml'
minmax = wxurl + '/' + 'minmax.txt'
wicon  = wxurl + '/' + 'icon.html'

# just for testing
USE_URL = True
xmlfile = '/home/wospi/wospi/backup/wxdata.xml'
txtfile = '/home/wospi/wospi/backup/minmax.txt'


# value to cloud coverage mapping in %
# just random values
forecast_value = { '8' : 0,
                   '6' : 25,
                   '2' : 75,
                   '3' : 85,
                   '18': 100,
                   '19': 100,
                   '7' : 40,
                   '22': 50,
                   '23': 60
                  }

#-------------------------------------------------------------------------------


def build_wospi_reply(root, country):
    """ read xml from ur and parse into dict
        read minmax and write some value into dict
        read conditions and write into dict
        Build final json for telefraf
    """

    # xml to dic 
    wxdata = {}

    # json for telefraf
    wospi_data = {}

    # find integer and foat values
    re_int   = re.compile('^[0-9]+$')
    re_float = re.compile('^[0-9]+\.\d+$')

    # get wxdata file and put into dictionary
    for wx in root:
        value = wx.text.strip()
        # ignor the 'bardata' values
        if wx.tag != "bardata":
            m = re.match(re_int, value)
            n = re.match(re_float, value)
            if m:
                if n:
                    wxdata[wx.tag] = float(value)
                else:
                    wxdata[wx.tag] = int(value)
            elif n:
                wxdata[wx.tag] = float(value)
            else:
                wxdata[wx.tag] = value


    # get minmax file
    minmax_val   = get_wospi_minmax(minmax)

    # get weather condition forecast
    wxdata['forecast'] = get_wospi_icon(wicon)


    # <timestamp>18.07.2024 13:37:39</timestamp>
    timestamp    = wxdata['timestamp']
    d            = datetime.strptime(timestamp, "%d.%m.%Y %H:%M:%S")
    epoch        = datetime.utcfromtimestamp(0)
    dt           = int((d - epoch).total_seconds())

    # get timezone diff in seconds
    tzinfo       = ZoneInfo('Europe/Vienna')
    dt_local     = datetime.now(tzinfo)
    tz_diff      = int(dt_local.utcoffset().total_seconds())
    current_date = timestamp.split()[0]
    wxdata['tz_diff'] = tz_diff

    # convert to epoch
    # utc
    wxdata['sunrise_utc']      = (int(datetime.strptime(current_date + ' ' + wxdata['sunrise_lt'] + ':00', '%d.%m.%Y %H:%M:%S').timestamp()) ) * 1000000000
    wxdata['sunset_utc']       = (int(datetime.strptime(current_date + ' ' + wxdata['sunset_lt']  + ':00', '%d.%m.%Y %H:%M:%S').timestamp())) * 1000000000
    # local time
    wxdata['sunrise_local']    = (int(datetime.strptime(current_date + ' ' + wxdata['sunrise_lt'] + ':00', '%d.%m.%Y %H:%M:%S').timestamp()) + tz_diff) * 1000000000
    wxdata['sunset_local']     = (int(datetime.strptime(current_date + ' ' + wxdata['sunset_lt']  + ':00', '%d.%m.%Y %H:%M:%S').timestamp()) + tz_diff) * 1000000000
    # for grafana
    wxdata['sunrise_corr']    = (int(datetime.strptime(current_date + ' ' + wxdata['sunrise_lt'] + ':00', '%d.%m.%Y %H:%M:%S').timestamp()) - tz_diff) * 1000000000
    wxdata['sunset_corr']     = (int(datetime.strptime(current_date + ' ' + wxdata['sunset_lt']  + ':00', '%d.%m.%Y %H:%M:%S').timestamp()) - tz_diff) * 1000000000

    wxdata['today_outtemp_min_c'] = float(minmax_val[1])
    wxdata['today_outtemp_max_c'] = float(minmax_val[2])

    # split into tokens
    LAT_s         =  minmax_val[4].split()
    LON_s         =  minmax_val[5].split()

    # create latitude and longitude string
    LAT           = LAT_s[1] + "'" + LAT_s[0]
    LON           = LON_s[1] + "'" + LON_s[0]
    wxdata['lat'] = float(DMS2dec(LAT))
    wxdata['lon'] = float(DMS2dec(LON))

    # 
    wxdata["cloudiness"]  = forecast_value[str(wxdata['fcicon'])]

    # build json
    wospi_data["country"] = country
    wospi_data["city"]    = minmax_val[3]
    wospi_data["v"]       = wxdata

    # print json to stdout
    print("[")
    print(json.dumps(wospi_data, indent = 2))
    print("]")

    return



#-------------------------------------------
def read_txtfile(infile):
    """ read any text file
    """
    try:
        with open(infile, 'r') as f:
            txt = f.readlines()

        f.close()
    except Exception as e:
        print('Done with exception(s): %s.' % e)
        errStat = 1
        sys.exit(errStat)

    return txt


def get_wospi_minmax(infile):
    """ reads the wospi minmax file from url
        extracts a few values
    """
    #     LOCATION: Hollabrunn, Austria (N 48&deg;33.82'  E 016&deg;05.504')</b>
    # <b>TEMPERATURE</b>  (Today's MIN @ 04:29 LT, MAX @ 14:53 LT)
    #  Today       MIN  15.4&deg;C / 59.8&deg;F          MAX  29.1&deg;C / 84.4&deg;F


    wospivers = ''
    location  = ''
    coord_lat = ''
    coord_lon = ''

    temp_min = 0
    temp_max = 0
    found_temp = False

    if USE_URL:
        try:
            response = requests.get(infile)
            minmax_data = response.text.splitlines()
        except:
            minmax = [wospivers, temp_min,  temp_max, location, coord_lat, coord_lon ]
            return minmax

    else:
        minmax_data = read_txtfile(infile)


    # match following string in the minmax file
    #   Software Version .... : 20151108-RPi
    re_version = re.compile('.*(Software\s+Version)\s+\.\..*:\s+(\w+)')
    for line in minmax_data:
        m = re.match(re_version, line)
        if m:
            wospivers = m.group(2)

    re_h_temp = re.compile('.*<b>TEMPERATURE</b>.*$')
    re_h_dew  = re.compile('.*<b>DEW POINT</b>.*$')
    re_h_loc  = re.compile('.*LOCATION:\s+(\w+),\s+.*\(([NS]\s+[0-9]+&deg;[0-9]+\.[0-9]+).*([EW]\s+[0-9]+&deg;[0-9]+\.[0-9]+).*$')
    re_temp   = re.compile('.*Today\s+MIN\s+(-?(0|[1-9]\d*\.\d+)?)&deg;C.*\s+MAX\s+(-?(0|[1-9]\d*\.\d+)?)&deg;C.*$')

    #print("DEBUG =========================================== loop ===========================================")
    #print(len(minmax_data))
    for line in minmax_data:
        #print("DEBUG: data: %s" % minmax_data)

        m = re.match(re_h_temp, line)
        if m:
            found_temp = True

        m = re.match(re_h_dew, line)
        if m:
            found_temp = False

        m = re.match(re_temp, line)
        if m and found_temp:
            temp_min = m.group(2)
            temp_max = m.group(4)

        m = re.match(re_h_loc, line)
        if m:
            location  = m.group(1)
            coord_lat = m.group(2).replace('&deg;','*')
            coord_lon = m.group(3).replace('&deg;','*')


    minmax = [wospivers, temp_min,  temp_max, location, coord_lat, coord_lon ]

    return minmax


def get_wospi_icon(infile):
    """ get alt text from html file
    """

    wicon_text = ''

    try:
        request = urllib.request.Request(infile,None,headers_agent)
        xml     = urllib.request.urlopen(request, timeout=10)
        soup    = BeautifulSoup(xml, 'lxml')

        for div in soup.find_all('div', 'forecastIcon'):
            img = div.find('img', alt=True)
            wicon_text = img['alt']
    except:
        wicon_text = ''

    return wicon_text



def split_lonlat(gps_coded):
    """ remove non numeric chars, split gps coordinates in single numeric parts
        http://stackoverflow.com/questions/10852955/python-batch-convert-gps-positions-to-lat-lon-decimals
    """

    # definition is wrong in the above link
    direction = {'N':1, 'S':-1, 'E':1, 'W':-1}
    # tokenize string
    gps_clean = gps_coded.replace(u'°',' ').replace('*', ' ').replace('\'',' ').replace('"',' ')
    gps_clean = gps_clean.split()
    # get wind direction
    gps_clean_dir = gps_clean.pop()
    # fill with zero values for easier calc of decimals
    gps_clean.extend([0,0,0])
    # add numeric factor for winddir
    gps_clean.append(direction[gps_clean_dir])
    gps_clean.append(gps_clean_dir)

    return gps_clean


def DMS2dec(DMS):
    """ convert gps DMS string to decimal
    """
    # repare string
    dms_l = split_lonlat(DMS)
    wdir_s = dms_l.pop()

    # calculate min from MM'SS"
    min_m  = float("%05.2f" % (float(dms_l[1]) + (float(dms_l[2])/60.0)))
    min_ms = modf(min_m)

    m = min_ms[1]/60
    s = min_ms[0]/60

    gps_dec = m + s


    # pad missing 0s
    # target format "ddmm.hhN/dddmm.hhW"
    if ((wdir_s == 'W') or (wdir_s == 'E')):
        deg = dms_l[0].zfill(3)
    else:
        deg = dms_l[0].zfill(2)

    # build result string
    dms = "{:0.4f}".format(int(deg) + gps_dec)

    return dms


#-------------------------------------------------------------------------------

def main():
    root = ''

    if USE_URL:
        request = urllib.request.Request(wxfile,None,headers_agent)
        xml     = urllib.request.urlopen(request, timeout=10)
        root    = ET.fromstring(xml.read())
    else:
        xml     = ET.parse(xmlfile)
        root    = xml.getroot()


    build_wospi_reply(root, tag_country)


#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

