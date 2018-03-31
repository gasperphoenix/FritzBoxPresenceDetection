# -*- coding: utf-8 -*-
"""Module for communication with a FritzBox.

This module provides an interface for communicating with a FritzBox.
"""

__author__     = "Dennis Jung"
__copyright__  = "Copyright 2017, Dennis Jung"
__credits__    = ["Dennis Jung"]
__license__    = "GPL Version 3"
__maintainer__ = "Dennis Jung"
__email__      = "Dennis.Jung@stressfrei-arbeiten.com"


#===============================================================================
# Imports
#===============================================================================
import argparse
import logging
import urllib.request
import hashlib
import re
import json
import time

from xml.dom import minidom

import xml.etree.ElementTree as ElementTree


#===============================================================================
# Evaluate parameters
#===============================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", 
                                     description="In case no option is selected the script will "
                                     "return the list of all known devices including their WLAN presence status. " 
                                     "If --name or --mac is specified it will return 'True' if the device is present, 'False' otherwise.")
    
    parser.add_argument('--v1', 
                      help='Debug level INFO', 
                      dest='verbose_INFO',
                      default=False,
                      action='store_true')
    parser.add_argument('--v2', 
                        help='Debug level ERROR', 
                        dest='verbose_ERROR',
                        default=False,
                        action='store_true')
    parser.add_argument('--v3', 
                        help='Debug level DEBUG', 
                        dest='verbose_DEBUG',
                        default=False,
                        action='store_true')
    
    parser.add_argument('-n',
                        '--name', 
                        help='Check presence of device identified by its name registered on the FritzBox', 
                        dest='name',
                        action='store')
    
    parser.add_argument('-c',
                        '--config', 
                        help='FritzBox configuration file. If not specified the default configuration '
                        'from the installation will be used.', 
                        dest='config',
                        action='store')
    
    args = parser.parse_args()


#===============================================================================
# Setup logger
#===============================================================================
if __name__ == '__main__':
    log_level = logging.CRITICAL
    
    if args.verbose_INFO: log_level = logging.INFO
    if args.verbose_ERROR: log_level = logging.ERROR
    if args.verbose_DEBUG: log_level = logging.DEBUG
    
#    logging.basicConfig(level=log_level,
#                        format="[{asctime}] - [{levelname}] - [{process}:{thread}] - [{filename}:{funcName}():{lineno}]: {message}",
#                        datefmt="%Y-%m-%d %H:%M:%S",
#                        style="{")

    logging.basicConfig(level=log_level,
                        format="[{asctime}] - [{levelname}]: {message}",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        style="{")
        
logger = logging.getLogger(__name__)


#===============================================================================
# Constant declarations
#===============================================================================
USER_AGENT = "Mozilla/5.0 (U; Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0"

# Structure of the WLAN device information  
WLAN_DEV_INFO = dict(
    WLAN_DEV_NAME=0,    # Device name
    WLAN_DEV_IP=1,      # Current device IP
    WLAN_DEV_MAC=2,     # Device HW MAC address
    WLAN_DEV_CON=3,     # WLAN connectivity information
    WLAN_DEV_ON_TS=4)   # Last WLAN presence timestamp


#===============================================================================
# Exceptions
#===============================================================================
class InvalidParameterError(Exception): pass


#===============================================================================
# Class definitions
#===============================================================================
class FritzBox():
    """Interface for communication with a FritzBox.
    
    This class provides an interface for communication with a FritzBox using LUA pages.
    """
    
    def __init__(self, configFile="../cfg/fritzbox.conf"):
        self.__configFile = configFile
        
        self.__readXMLConfigFritzBox()
        
        self.sid = ''
        
        self.deviceList = {}
        
        self.chk_ts = 0
    
    
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
        
        logger.debug("Read XML configuration for the FritzBox")
        
        tree = ElementTree.parse(self.__configFile)
        
        root_element = tree.getroot()
        
        self.__server = str(root_element.find("ip").text)
        self.__port = str(root_element.find("port").text)
        self.__password = str(root_element.find("password").text)
    
    
    def loadFritzBoxPage(self, url, param):
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
        
        logger.debug("Load the FritzBox page: " + pageUrl)
        
        headers = { "Accept" : "application/xml",
                    "Content-Type" : "text/plain",
                    "User-Agent" : USER_AGENT}
    
        request = urllib.request.Request(pageUrl, headers = headers)
        
        try:
            response = urllib.request.urlopen(request)
        except:
            logger.error("Loading of the FritzBox page failed: %s" %(pageUrl))
            
            return None
        
        page = response.read()
        
        if (response.status != 200):
            logger.error("Unexpected feedback from FritzBox received: %s %s" % (response.status, response.reason))
                        
            return None
        else:  
            return page
    
    
    def login(self):
        """Authenticate with the FritzBox to access private pages.
        
        The method authenticates with a FritzBox using the authentication credentials
        read out from the configuration file during the class object instantiation.
        
        Args:
            Does not require any arguments.

        Returns:
            Does not return any value.
        """
        
        logger.debug("Login to the FritzBox")
        
        headers = { "Accept" : "application/xml",
                    "Content-Type" : "text/plain",
                    "User-Agent" : USER_AGENT}

        pageUrl = 'http://' + self.__server + ':' + self.__port + '/login_sid.lua'
    
        request = urllib.request.Request (pageUrl, headers = headers)
    
        try:
            response = urllib.request.urlopen(request)
        except:
            logger.error("Loading of the FritzBox page failed: %s" %(pageUrl))
            
            return False
        
        page = response.read()
    
        if (response.status != 200):
            logger.error("Unexpected feedback from FritzBox received: %s %s" % (response.status, response.reason))
            
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
                logger.debug("Authentication succeeded")
                
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
            logger.error("Unexpected feedback from FritzBox received: %s %s" % (response.status, response.reason))
            
            return False
        else:
            sid = re.search(b'<SID>(.*?)</SID>', page).group(1)
            
            if (sid == "0000000000000000"):
                logger.error("Authentication failed due to invalid password")
                
                return False
            else:
                logger.debug("Authentication succeeded")
                
                self.sid = sid
                
                return True
        
    
    def isDevicePresent(self, deviceName=None, debounceOff=0):
        """Check if the given device is currently in WLAN access range -> device is present.
        
        The method checks if the specified device is currently in WLAN access range of the FritzBox
        to determine if it is present or not. You can optionally specify a debounce time for the transition
        to the absent state. This is helpful if you observe sporadic absent detections e.g. for iPhone
        devices.
                
        Args:
            deviceName (str): Device that shall be checked.
            debounceOff (int):  Debounce transition to absent by this no. of minutes
            
        Raises:
            UnknownDeviceError: If the given device is not registered with the FritzBox 

        Returns:
            If the device is registered with the FritzBox the method will return True if the device is present, False otherwise.
        """
        
        devices, chk_ts = self.getWLANDeviceInformation()
        
        if deviceName is not None:
            logger.debug("Check if the device " + deviceName + " is present")
            
            if deviceName in devices:
                if chk_ts - devices[deviceName]['on_ts'] == 0:
                    return True # Device is present
                elif chk_ts - devices[deviceName]['on_ts'] <= 60 * debounceOff:
                    return True # Device is absent less than the defined debounce time
                else:
                    return False # Device is absent for more than the defined debounce time
            else:
                return False # Device is not listed and therefore not present
        else:
            raise InvalidParameterError()
        
        return False

        
    def getWLANDeviceInformation(self):
        """Query WLAN information for all FritzBox known devices.
        
        The method queries all WLAN related information for all devices known to the FritzBox.
        
        Args:
            None

        Returns:
            deviceList (List): List with all devices and information as two-dimensional matrix. The parameters for each device
                               are accessible using the index FB_WLAN_DEV_INFO elements.
                        
            chk_ts (float):    Timestamp of the last presence check
        """
        
        logger.debug("Load WLAN device information from the FritzBox for all known devices")
        
        self.chk_ts = time.time()
        
        page = self.loadFritzBoxPage('/data.lua', 'lang=de&no_sidrenew=&page=wSet')

        jsonStructure = json.loads(page.decode('UTF-8'))
        
        jsonStructure_devices = jsonStructure['data']['net']['devices']
        
        for i in range(len(jsonStructure_devices)):
            name = jsonStructure_devices[i]['name']
            on_ts = self.chk_ts
            
            self.deviceList[name] = {'on_ts' : on_ts}
                
        return self.deviceList, self.chk_ts
            

#===============================================================================
# Main program
#===============================================================================
def main():    
    fb = FritzBox(args.config)
    
    if (fb.login()):
        if (args.name == None):
            devices, chk_ts = fb.getWLANDeviceInformation()
            
            print(devices)
            
        elif (args.name != None):
            print(fb.isDevicePresent(deviceName=args.name))
        
    
if __name__ == '__main__':
    main()