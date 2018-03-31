# FritzBox Presence Detection

This module brings reliable presence detection for all WLAN devices (including iPhone) that can also be used on a Raspberry Pi.

The task to setup a reliable presence detection for devices that can be used eg. to check if a person is present (by checking mobile phone presence) is not easy. You can ping mobile devices which works for most device types but eg. iPhone devices will enter stealth mode after approx. 10 minutes if the screen is locked. Therefore these devices will be wrongly detected as absent if you ping them. So I started developing another solution. I figured out that my FritzBox is capable to detect the presence status of all WLAN devices (incl. iPhone devices) in a reliable manner with an approx. 1 minutes delay. As outcome I developed this module that  logs into your FritzBox and checks the device availability using the FritzBox WLAN connectivity information. 

The module can be used both as module to be imported in other Python modules or as standalone script.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

- Python 3

### Installing

Get a local copy of the repository master branch by downloading the zip archive from Github. Alternatively you can clone the git repository.

```
wget https://github.com/gasperphoenix/FritzBoxPresenceDetection/archive/master.zip
```

Extract the archive content to a local folder.

Open the file cfg/fritzbox.conf to enter your credentials for accessing your FritzBox.

```
<?xml version="1.0" encoding="UTF-8"?>

<fritzbox>
	<ip>192.168.0.1</ip>           // Your FritzBox IP goes here 
	<port>80</port>                // Usually port 80 should be ok
	<password>pass</password>      // Your FritzBox password goes here
</fritzbox>
```

### Usage as Command Line Tool

The script includes a help that will be printed on the console if you call it with the parameter '--help'.

```
$ python3 FritzBox.py --help

usage: FritzBox.py [options]

In case no option is selected the script will return the list of all known
devices including their WLAN presence status. If --name or --mac is specified
it will return 'True' if the device is present, 'False' otherwise. Debouncing
of the transitions to absent is not supported if the script is used as command
line tool.

optional arguments:
  -h, --help            show this help message and exit
  --v1                  Debug level INFO
  --v2                  Debug level ERROR
  --v3                  Debug level DEBUG
  -n NAME, --name NAME  Check presence of device identified by its name
                        registered on the FritzBox
  -c CONFIG, --config CONFIG
                        FritzBox configuration file. If not specified the
                        default configuration from the installation will be
                        used.
```

You can eg. check the WLAN device presence of the device 'YourDevice' with the following command line.

```
$ python3 FritzBox.py --name YourDevice

True
```


### Usage as import module
Three steps are required to check the presence of a device:

Step 1: Create class instance

```
fb = FritzBox.FritzBox()
```

Step 2: Authenticate with the FritzBox

```    
fb.login()
```

Step 3: Check the presence of a device. Make sure to use exactly the same device name that is listed on your FritzBox pages. The method will return 'True' if your device is connected, otherwise 'False'.

```
fb.isDevicePresent('YourDevice')
```

Putting it all together:
```
import FritzBox

fb = FritzBox.FritzBox()

if (fb.login()):
	print(fb.isDevicePresent('YourDevice'))
```

## Authors

* **Dennis Jung** - *Repository owner* - [Stressfrei-arbeiten.com](https://stressfrei-arbeiten.com)

See also the list of [contributors](https://github.com/gasperphoenix/FritzBoxPresenceDetection/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007 - see the [LICENSE.md](LICENSE.md) file for details