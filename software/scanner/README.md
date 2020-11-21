# Software Running on each Raspberry Pi for Scanning and Communication Tasks

## Enable I2C, SPI and SSH
```sh
sudo raspi-config
```


## Install dependencies 
Install requirements of python scanner

```sh
python3 -m pip install -r requirements.txt
```

```sh
sudo apt install nmap
```

## Enable booth SPI in bootconfig

```sh
dtparam=spi=on
dtoverlay=spi1-3cs
```

## Enabling autostart

```sh
sudo vim /etc/rc.local
```

```sh
cd /home/pi/gits/networkScanner/software/scanner/
python3 scanner.py
```

## Generating certificates for the Office HTTPs webside

```sh
mkdir certs
cd certs
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```
