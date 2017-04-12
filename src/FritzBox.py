# -*- coding: utf-8 -*-
"""FritzBox.py module documentation

This module provides an interface for communication with a FritzBox.
"""

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
    """Class for communication with a FritzBox
    
    Public interfaces:
        login()
            Authenticate with the FritzBox to access private pages
            
        isDeviceConnected(deviceName)
            Check if the given device is currently in WLAN access range -> device is present
    """
    
    def __init__(self):
        self.__readXMLConfigFritzBox()
        
        self.sid = ''
    
    
    def __del__(self):
        pass
    
    
    def __readXMLConfigFritzBox(self):
        """Method to read in the FritzBox authentication credentials from the configuration file.
        
        The method reads out the FritzBox authentication credentials from the configuration file.
        
        Args:
            Requires no arguments.

        Returns:
            Returns no value.
        """
        
        tree = ElementTree.parse(CONFIG_FILE_FRITZ_BOX)
        
        root_element = tree.getroot()
        
        self.__server = str(root_element.find("ip").text)
        self.__port = str(root_element.find("port").text)
        self.__password = str(root_element.find("password").text)
    
    
    def __loadFritzBoxPage(self, url, param):
        """Method to read out a page from the FritzBox.
        
        The method reads out the given page from the FritzBox. It automatically includes a session id
        between url and param.
        
        Args:
            url (str):   URL of the page that shall be read out from the FritzBox.
            param (str): Additional parameters that shall be added to the URL.

        Returns:
            Requested page as string, None otherwise.
        """
        
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
        """Authenticate with the FritzBox to access private pages.
        
        The method authenticates with a FritzBox using the authentication credentials
        read out from the configuration file during the class object instantiation.
        
        Args:
            Does not support any arguments.

        Returns:
            Does not return any value.
        """
        
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
        """Check if the given device is currently in WLAN access range -> device is present.
        
        The method checks if the specified device is currently in WLAN access range of the FritzBox
        to determine if it is present or not.
        
        Args:
            deviceName (str): Device that shall be checked.

        Returns:
            True if the device is present, False otherwise.
        """
        
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
    """Main method for testing purposes and usage example.
        
        The method is used for testing of the module functionality and to provide
        an usage example.
        
        Args:
            Requires no arguments.

        Returns:
            Returns no value.
    """
    
    fb = FritzBox()
    
    fb.login()
    
    while True:
        print ('Is YourDevice connected: %1s' % fb.isDeviceConnected('YourDevice'))
        time.sleep(5)
        
    
if __name__ == '__main__':
    main()