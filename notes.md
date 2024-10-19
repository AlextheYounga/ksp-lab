# Notes

## target pitch and heading
- higher y value means south
- tells you on the spinny ball


## Scraps
```py
# Deploy antennas
# This drains all batteries on the zmap satellite if there is no sun
for antenna in vessel.parts.antennas:
    if antenna.deployable:
        antenna.deployed = True
time.sleep(1)
```


