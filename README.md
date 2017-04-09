# FritzBoxPresenceDetection

This module brings reliable presence detection for all WLAN devices (including iPhone) that can also be used on a Raspberry Pi.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

- Python 3

### Installing

A step by step series of examples that tell you have to get a development env running

Get a local copy of the repository master development by downloading the zip archive from Github. Alternatively you can clone the git repository.

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

Step 3: Check presence of a device. Make sure to use exactly the same device name that is listed on your FritzBox pages. The method will return 'True' if your device is connected, otherwise 'False'.

```
fb.isDeviceConnected('YourDevice'))
```

## Authors

* **Dennis Jung** - *Repository owner* - [Stressfrei-arbeiten.com](https://stressfrei-arbeiten.com)

See also the list of [contributors](https://github.com/gasperphoenix/FritzBoxPresenceDetection/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007 - see the [LICENSE.md](LICENSE.md) file for details