# -*- coding: utf-8 -*-
# FritzBox.py: Interface module for communication with the FritzBox

__author__     = "Dennis Jung"
__copyright__  = "Copyright 2017, Dennis Jung"
__credits__    = ["Dennis Jung"]
__license__    = "GPL Version 3"
__version__    = "1.0.0"
__maintainer__ = "Dennis Jung"
__email__      = "Dennis.Jung@stressfrei-arbeiten.com"
__status__     = "Development"


#===============================================================================
# Imports
#===============================================================================
import urllib.request
import hashlib
import re
import sys
import time

from xml.dom import minidom

import xml.etree.ElementTree as ElementTree


#===============================================================================
# Constant declarations
#===============================================================================
USER_AGENT = "Mozilla/5.0 (U; Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0"
CONFIG_FILE_FRITZ_BOX = "../cfg/fritzbox.conf"


#===============================================================================
# Start of program
#===============================================================================
class FritzBox():
    def __init__(self):
        self.__readXMLConfigFritzBox()
        
        self.sid = ''
    
    
    def __del__(self):
        pass
    
    
    def __readXMLConfigFritzBox(self):
        
        tree = ElementTree.parse(CONFIG_FILE_FRITZ_BOX)
        
        root_element = tree.getroot()
        
        self.__server = str(root_element.find("ip").text)
        self.__port = str(root_element.find("port").text)
        self.__password = str(root_element.find("password").text)
    
    
    def __loadFritzBoxPage(self, url, param):
        pageUrl = 'http://' + self.__server + ':' + self.__port + url + "?sid=" + self.sid.decode('utf-8') + param
        
        headers = { "Accept" : "application/xml",
                    "Content-Type" : "text/plain",
                    "User-Agent" : USER_AGENT}
    
        request = urllib.request.Request(pageUrl, headers = headers)
        
        response = urllib.request.urlopen(request)
        
        page = response.read()
        
        if (response.status != 200):
            print( "%s %s" % (response.status, response.reason))
            
            print(page) 
            
            return None
        else:  
            return page
    
    
    def login(self):
        headers = { "Accept" : "application/xml",
                    "Content-Type" : "text/plain",
                    "User-Agent" : USER_AGENT}

        pageUrl = 'http://' + self.__server + ':' + self.__port + '/login_sid.lua'
    
        request = urllib.request.Request (pageUrl, headers = headers)
    
        response = urllib.request.urlopen(request)
        
        page = response.read()
    
        if (response.status != 200):
            print( "%s %s" % (response.status, response.reason))
            
            print(page)
            
            return False
        else:
            pageXml = minidom.parseString(page)
            
            sidInfo = pageXml.getElementsByTagName('SID')
            
            sid = sidInfo[0].firstChild.data
            
            if (sid == "0000000000000000"):   
                challengeInfo = pageXml.getElementsByTagName('Challenge')
                
                challenge = challengeInfo[0].firstChild.data
                
                challenge_bf = (challenge + '-' + self.__password).encode( 'utf-16le' )
                
                m = hashlib.md5()
                
                m.update(challenge_bf)
                
                response_bf = challenge + '-' + m.hexdigest().lower()
                
            else:
                self.sid = sid
                
                return True
                                        
        headers = { "Accept" : "text/html,application/xhtml+xml,application/xml",
                    "Content-Type" : "application/x-www-form-urlencoded",
                    "User-Agent" : USER_AGENT}

        pageUrl = 'http://' + self.__server + ':' + self.__port + "/login_sid.lua?&response=" + response_bf
    
        request = urllib.request.Request(pageUrl, headers = headers)
    
        response = urllib.request.urlopen(request)
    
        page = response.read()    
        
        if (response.status != 200):
            print( "%s %s" % (response.status, response.reason))    
            
            print(page)
            
            return False
        else:
            sid = re.search(b'<SID>(.*?)</SID>', page).group(1)
            
            if (sid == "0000000000000000"):
                print("ERROR - No SID received because of invalid password")
                
                sys.exit(0)
            else:
                self.sid = sid
                
                return True
        
    
    def isDeviceConnected(self, deviceName):
        page = self.__loadFritzBoxPage('/data.lua', 'lang=de&no_sidrenew=&page=wSet')

        deviceTable = re.findall(r'<table id="uiWlanDevs".*?>.*?</table>', str(page), re.MULTILINE|re.DOTALL)
        
        deviceTableBody = re.findall(r'<tbody>.*?</tbody>', str(deviceTable), re.MULTILINE|re.DOTALL)
        
        devicesSections = re.findall(r'<tr.*?>.*?</tr>', str(deviceTableBody), re.MULTILINE|re.DOTALL)
        
        devices = re.findall(r'<td.*?>(.*?)</td>', str(devicesSections), re.MULTILINE|re.DOTALL)
                
        for i in range(len(devices) // 7):
            if (deviceName in devices[1 + i * 7]):
                if ("nicht verbunden" in devices[5 + i * 7]):
                    return False
                else:         
                    return True

    
def main():
    fb = FritzBox()
    
    fb.login()
    
    while True:
        print ('Is YourDevice connected: %1s' % fb.isDeviceConnected('YourDevice'))
        time.sleep(5)
        
    
if __name__ == '__main__':
    
    main()