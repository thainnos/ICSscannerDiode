#!/usr/bin/env python3

import os, sys, time
import _thread
import logging
from netaddr import *
import spidev
import coloredlogs
import configparser
import nmap
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont
import array
import RPi.GPIO as GPIO
import numpy as np
from flask import Flask, jsonify, render_template, redirect, json, request
import pandas as pd 
from io import StringIO
from flask_sslify import SSLify

# Flask 
app = Flask(__name__)
sslify = SSLify(app)

# Logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=logger)

# GPIO
GPIO.setmode(GPIO.BCM)

# Parameters
MESSAGE_SIZE = 2048

# Global Variables
scanRunning = 0
results = "" 

# SPI
spi1 = spidev.SpiDev()
spi2 = spidev.SpiDev()

# Scan arguments
scan_args = [
"-p 22", # SSH
"-p 80", # HTTP
"-p 443", # HTTPS
"--script s7-info.nse -p 102", # Siemens S7Com
"--script pcworx-info -p 1962", # Phoenix Contacts PC Worx
"--script modbus-discover.nse -p 502", # Modbus/TCP
"--script knx-gateway-discover -p 3671", # KNX
"--script snmp-info -p 161", # SNMP INFO
"--script nse/codesys-v2-discover.nse -p 1200", # Codesys
"--script nse/codesys-v2-discover.nse -p 2455", # Codesys
"--script  enip-info -sU -p 4481", # Ethernet/IP
"--script bacnet-info -sU -p 47808 ", # Bacnet
"--script bacnet-info -sU -p 47808 ", # Bacnet
"--script nse/dnp3-info.nse -p 20000 ", # dnp3
"--script nse/fox-info.nse -p 1911 ", # FOX
"-Pn -n -d --script nse/iec-identify.nse  --script-args='iec-identify.timeout=1000' -p 2404 ", # IEC
"-sU --script nse/moxa-enum.nse -p 4800 ", # MOXA
"--script nse/omrontcp-info.nse -p 9600 ", # OMRON TCP
"--script nse/omronudp-info.nse -sU -p 9600 ", # OMRON UDP
#"-p 0-65535" # All
] 

def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "displayConnected", "True")
    config.set("Settings", "spiConnected", "True")
    config.set("Settings", "packetsPerSecond", "10")
    config.add_section("Scan")
    config.set("Scan", "hosts", "127.0.0.1/24")
    with open(path, "w") as config_file:
        config.write(config_file)


def get_config(path):
    if not os.path.exists(path):
        create_config(path)

    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_setting(path, section, setting):
    config = get_config(path)
    value = config.get(section, setting)
    return value

# Send over SPI
def spiSend(spiPort, message="ttest"):
    message = list(message)
    if len(message) > MESSAGE_SIZE:
        message = message[:MESSAGE_SIZE]
        logging.error("Message to long and is now: " + str(message))
    data = message + (["\0"] * (MESSAGE_SIZE-len(message)))
    data = [int(ord(c)) for c in ''.join(data)]
    time.sleep(0.1)
    transmitted = spiPort.xfer(data)
    time.sleep(0.1)
    logger.debug("Transmitting over SPI. Transmitted: " + str(len(transmitted)))
    time.sleep(0.1)  

# drawScan function
def drawScan(host="0.0.0.0", scan_argument="", status="unknown"):  
  try:
    with canvas(device, dither=True) as draw:
      if deviceID == 1:
        draw.text((1, 0), "Ind. Scanner Office", fill="white", font=FontTemp)
      if deviceID == 2:
        draw.text((1, 0), "Ind. Scanner ICS", fill="white", font=FontTemp)
      draw.text((1, 10), "Scan: " + str(host), fill="white", font=FontTemp)
      draw.text((1, 20), "Args: " + str(scan_argument[-14:]), fill="white", font=FontTemp)
      draw.text((1, 30), "Stat: " + str(status), fill="white", font=FontTemp)
  except Exception as e:
    logger.error("Problem printing on display")

# draw function
def draw(status="unknown", freeText=""):  
  try:
    with canvas(device, dither=True) as draw:
      if deviceID == 1:
        draw.text((1, 0), "Ind. Scanner Office", fill="white", font=FontTemp)
      if deviceID == 2:
        draw.text((1, 0), "Ind. Scanner ICS", fill="white", font=FontTemp)
      draw.text((1, 30), "Stat: " + str(status), fill="white", font=FontTemp)
      draw.text((1, 40), str(freeText), fill="white", font=FontTemp)
  except Exception as e:
    logger.error("Problem printing on display")

# Main scanning function
def scanning_function(threadName, deviceID):
  nm=nmap.PortScanner()

  while True:
    while scanRunning == 0:
      time.sleep(1)
    for host in hosts:
      logger.info("Scanning:" + str(host))
      if scanRunning == 0:
        break
      for scan_argument in scan_args:
        drawScan(host, scan_argument, "scanning")
        time.sleep(1/int(packetsPerSecond))
        scan = nm.scan(str(host), arguments=str(" --max-rate " + str(packetsPerSecond) + " " + str(scan_argument)))
        logger.info('----------------------------------------------------')
        # print
        logger.info(nm.scaninfo())
        # print result as CSV
        logger.info(nm.command_line() )
        logger.info(str(nm.csv()))
        spiSend(spi2, str("r" + str(nm.csv())))
        #spiSend(spi2, str("r" + str(scan)))
        if scanRunning == 0:
          break
    draw("scanning finished", " :-) ")


# LED thread function
def led_function(threadName, delay):
  while True:
    GPIO.output(12, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(12, GPIO.LOW)
    time.sleep(delay)

# Read Results from SPI
def results_function(threadName, deviceID):
  global results
  first = 1
  while True:
    try:
      dataRecv = [0]
      datarecv = spi2.readbytes(MESSAGE_SIZE)
      datarecv_len = np.count_nonzero(datarecv)
      datarecv_str = str(''.join(chr(i) for i in datarecv))[:datarecv_len]
      logger.debug("spi2: " + datarecv_str)
      logger.debug("len(spi2): " + str(datarecv_len))
      if datarecv_len > 10:
        if datarecv_str[0] == 'r':
            if first == 1:
              results = str(datarecv_str)[1:] + "\n"
              first = 0
            else:
              results = results + str(datarecv_str)[1:].splitlines()[1] + "\n" 
      time.sleep(1)
    except Exception as e:
      logger.error("Error in SPI results function: " + str(e))

# Webserver thread
def webserver_function(threadName, deviceID):
  # Run the webserver.
  time.sleep(20)
  app.run(ssl_context=('certs/cert.pem', 'certs/key.pem'), host="0.0.0.0", port=443)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/scan')
def scan():
  return render_template('scan.html')

@app.route('/startscan')
def startscan():
  logging.debug("Scanning start requested")
  draw("scanning")
  spiData = list("sstart")
  spiSend(spi1, spiData)
  time.sleep(1)
  spiSend(spi1, spiData)
  return render_template('scan.html')

@app.route('/stopscan')
def stopscan():
  logging.debug("Scanning stop requested")
  draw("stop scanning")
  spiData = list("sstop")
  spiSend(spi1, spiData)
  time.sleep(1)
  spiSend(spi1, spiData)
  return render_template('scan.html')

@app.route('/scanresults')
def scanresulst():
  global results
  if len(results) > 0:
    a = pd.read_csv(StringIO(results),sep=";")
    restable = a.to_html(classes='table table-striped table-hover') 
  else:
    restable = "No scandata available"
  print(restable)
  return render_template('scanresults.html', restable = restable)

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/logout')
def logout():
  return render_template('logout.html')

# MAIN program start
if __name__== "__main__":
  if len(sys.argv) < 1:
    [inifile] = sys.argv[1:]
  else:
    inifile = "settings.ini"
  displayConnected = get_setting(inifile, 'Settings', 'displayConnected')
  spiConnected = get_setting(inifile, 'Settings', 'spiConnected')
  packetsPerSecond = get_setting(inifile, 'Settings', 'packetsPerSecond')
  hosts = get_setting(inifile, 'Scan', 'hosts')
  hosts = IPNetwork(str(hosts))

  # Set inputs
  GPIO.setup(26, GPIO.IN)
  GPIO.setup(27, GPIO.IN)

  # Set outputs
  GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(8, GPIO.OUT, initial=GPIO.HIGH)

  GPIO.output(12, GPIO.HIGH)
  GPIO.output(13, GPIO.HIGH)

  # Read Device ID
  deviceID = 0
  if GPIO.input(26):
    deviceID += 1
  if GPIO.input(27):
    deviceID =+ 2
  
  logging.info("Device ID is " + str(deviceID))

  # Check if script is executed as root
  if not os.geteuid()==0:
    sys.exit('This network scanner script must be run as root!')
  # Start LED thread
  _thread.start_new_thread(led_function, ("LED_Thread", 1, ) )
  time.sleep(1)
  GPIO.output(13, GPIO.LOW)

  # Clear the SPI Device if connected
  if displayConnected == "True":
    try:
      serial = i2c(port=1, address=0x3C)
      device = sh1106(serial, width=128, height=64, mode=1, rotate=2)
      FontTemp = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10, encoding="unic")
      draw("initializing", "")
    except Exception as e:
       logger.error("I2C SH1106 seems not to be connected: " + str(e))
  if spiConnected == "True":
    try:
      spiData = ["0"] * MESSAGE_SIZE
      spi1.open(0, 0)
      spi1.no_cs = False
      spi1.cshigh = False
      spi1.lsbfirst = False
      spi1.mode = 0b00
      spi1.max_speed_hz = 3900000
      spi2.open(1, 0)
      spi2.no_cs = False
      spi2.cshigh = False
      spi2.lsbfirst = False
      spi2.mode = 0b00
      spi2.max_speed_hz = 3900000
      _thread.start_new_thread(webserver_function, ("Webserver_Thread", deviceID) )
      if deviceID == 1:
        logging.info("Raspberry Pi on OFFICE side")
        logging.info("OOOO  FFFF  FFFF  I  CCCC  EEEE ")
        logging.info("O  O  F     F     I  C     E    ")
        logging.info("O  O  FFF   FFF   I  C     EEEE ")
        logging.info("O  O  F     F     I  C     E    ")
        logging.info("OOOO  F     F     I  CCCC  EEEE ")
        time.sleep(10) # Necessary for ICS Pi to boot up
        _thread.start_new_thread(results_function, ("Result_Thread", deviceID) )
        spiData = list("tTestmessage to check the communication chain. This is just forwarded through all devices.")
        draw("sending test message")
        spiSend(spi1, spiData)
        time.sleep(1)
        draw("ready")
        while True:
          time.sleep(60)
          logging.debug("Office Python alive message")
          

      elif deviceID == 2:
        logging.info("Raspberry Pi on ICS side")
        logging.info("I  CCCC  SSSS ")
        logging.info("I  C     S    ")
        logging.info("I  C     SSSS ")
        logging.info("I  C        S ")
        logging.info("I  CCCC  SSSS ")
        _thread.start_new_thread(scanning_function, ("Scanning_Thread", deviceID) )
        draw("ready")
        while True: # loop until first message is recieved
          datarecv = spi1.readbytes(MESSAGE_SIZE)
          datarecv_len = np.count_nonzero(datarecv)
          datarecv_str = str(''.join(chr(i) for i in datarecv))
          time.sleep(1)
          logger.debug("spi1: " + datarecv_str)
          logger.debug("len(spi1): " + str(datarecv_len))
          if datarecv[0] == 't':
            spiSend(spi2, datarecv_str)
            draw("test message recieved", "waiting for start")
          elif ("sstart" in datarecv_str):
            logger.debug("Starting scanning")
            draw("scanning")
            scanRunning = 1
          elif ("sstop" in datarecv_str):
            logger.debug("Stop scanning")
            draw("scanning stopped")
            scanRunning = 0
      
    except Exception as e:
       logger.error("SPI could not be initialized: " + str(e))
  



