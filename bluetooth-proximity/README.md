This is a bluetooth device tracker. Go into examples and run "python invasion <address> <loops>" and it will tell you how far the bluetooth device is from you. basically find a large square area, and walk in a square. press enter every time you hit a corner and it will tell you where the device is.

Requires linux to run. Also note that tx_power is a constant that the user must define, as it is machine and bluetooth dongle specific.

The base of this, bluetooth-proximity, is a repo found here:
https://github.com/dagar/bluetooth-proximity
It provides the utility functions for getting bluetooth rssi.

Why this is a security concern:
Using this sort of app would aid in invading a location for attackers. They can case the area, and find the devices inside. Running hcitool scan works to find all the devices in the area, but doesn't tell you where they are. This tool could.
Also this could be used during more physically oriented CTF matches where you're allowed to steal devices. This could help teams steal those devices in order to break past the defenses somewhere else. If these kind of hackathons aren't a thing, they should be.
From my research there is not way to hide your RSSI for bluetooth, so the best way to defend against something like this
