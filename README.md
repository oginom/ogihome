# ogihome

add following lines to `/etc/mosquitto/mostuitto.conf` to allow all access from LAN

```conf
allow_anonymous true
listener 1883 0.0.0.0
```

## workaround for raspi

```sh
# need for numpy
sudo apt-get install libatlas-base-dev
```
