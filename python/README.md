# Dragos Portal Python API

A simple Python wrapper client for the Dragos portal API

## Usage
Setup a config file as shown below. The example scripts are designed to be called via cron (or any scheduler).
We recommend a frequency of once a day (please choose a random time of day to execute on, i.e. 3:38am instead of 00:00).
The example scripts are meant to be used as a starting point for your own integration, so please modify according to your own needs.

See your user profile page on portal.dragos.com for more information, to generate API keys, or to request assistance.

## Config
`dragos.cfg`:
```ini
[dragos portal]
access_token = <Hex token>
access_key = <Base64 key>
```
(no quotes in config)


## API docuementation
https://portal.dragos.com/api/v1/doc/
