# FritzBoxPresenceDetection

This module brings reliable presence detection for all WLAN devices (including iPhone) that can also be used on a Raspberry Pi.

The task to setup a reliable presence detection for devices that can be used eg. to check if a person is present (by checking mobile phone presence) is not easy. You can ping mobile devices which works for most device types but eg. iPhone devices will enter stealth mode after approx. 10 minutes if the screen is locked. Therefore these devices will be wrongly detected as absent if you ping them. So I started developing another solution. I figured out that my FritzBox is capable to detect the presence status of all WLAN devices (incl. iPhone devices) in a reliable manner with an approx. 1 minutes delay. As outcome I developed this module that  logs into your FritzBox and checks the device availability using the FritzBox WLAN connectivity information. 

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

Open the file cfg/fritzbox.conf to enter you credentials for accessing your FritzBox.

```
<?xml version="1.0" encoding="UTF-8"?>

<fritzbox>
	<ip>192.168.0.1</ip>           // Your FritzBox IP goes here 
	<port>80</port>                // Usually port 80 should be ok
	<password>rob2okt.</password>  // Your FritzBox password goes here
</fritzbox>
```

Three steps are required to check the presence of a device:

Step 1: Create class instance

```
fb = FritzBox()
```

Step 2: Authenticate with the FritzBox

```    
fb.login()
```

Step 3: Check the presence of a device. Make sure to use exactly the same device name that is listed on your FritzBox pages. The method will return 'True' if your device is connected, otherwise 'False'.

```
fb.isDeviceConnected('YourDevice'))
```

## Authors

* **Dennis Jung** - *Repository owner* - [Stressfrei-arbeiten.com](https://stressfrei-arbeiten.com)

See also the list of [contributors](https://github.com/gasperphoenix/FritzBoxPresenceDetection/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007 - see the [LICENSE.md](LICENSE.md) file for details