# ogihome

add following lines to `/etc/mosquitto/mostuitto.conf` to allow all access from LAN

```
allow_anonymous true
listener 1883 0.0.0.0
```
