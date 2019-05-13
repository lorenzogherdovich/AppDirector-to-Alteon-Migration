# AppDirector-to-Alteon-Migration 

## Table Of Contents ###
- [Description](#description )
- [How To Use](#how-to-use )
  * [Running Manually Using Python](#running-manually-using-python)
- [Currently Supported](#currently-supported)
- [Planed In The Future](#planed-in-the-future)

## Description ##
The following script is used to migrate AppDirector Version 2.14 configuration to Alteon configuration.
Manual use was tested on both Linux and windows client(using Pycharm)
Currently we only support AppDirector version 2.14 .
Supported Alteon versions are 32.0.0.0 and above (not tested on older versions)
The script works with both appdirector config file that not contains “/” at the end of the line.

## How To Use ##

### Running Manually Using Python ###
In order to use the script, make sure you have installed python2
At the “file and path” section you should add version ID and file path that contain both the script at the AppDirector config file.
In order not to type the AppDirector file name at each execution you can add it manually. (change the file name at ‘filetosearch’ object).

## Currently Supported ##
- Vlan
- Layer3 interfaces
- Reals 
  * Real IP
  * Ena/dis
  * Backup server
- Groups
  * Metric
  * Backup group creation
  * Real server attachment
  * Backup group attachment
- Virts
  * VIP
  * Service and service type
  * Group attachment

## Planed in The Future ##
* Persistence
  * Client IP
  * cookie
* Trunks / LACP
* Static Routes
* syslog
* NTP
* SNMP
* Filters
* HA
  * VRRP migration into new HA
  * Floating IP
* Health Checks
  * Servers HC
  * Groups HC
* NAT
  * Client NAT IP
  * Client NAT range
  * Client range to be NAT
* XFF
* SIP LB
* Segmentation
