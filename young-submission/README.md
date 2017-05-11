Young's Submission

My efforts for this project consisted of two major parts. First, I tried to use
an Adafruit Bluefruit LE Sniffer to sniff Bluetooth Low Energy (BLE) packets
from a Bluetooth mouse. I did this using their Python API [1]. Unfortunately,
packets were not being decrypted correctly by the API, and I spent a while
trying to figure out why, but ultimately could not resolve the problem. A
packet capture file that I captured with the sniffer can be found in the git
repository, as capture.pcap. However, if you open it in Wireshark, you will see
that the data is often interpreted as "Unknown data" and the contents are
random bytes. I didn't write any code for this part, but I did spend plenty of
time troubleshooting.

The second part of my contribution was to reverse engineer the communications
between the mouse and my laptop. However, since I couldn't decrypt the packet
contents, I couldn't analyze that particular communication. Instead, I decided
to write a parser in Python that can take a pcap file of decrypted BLE packets
process it, and generate some basic statistics and information about it. I
tested it with Mike Ryan's sample pcap files[2] that he provides with his
`crackle` program that can decrypt encrypted BLE communication.

For my script, btle-parse.py, running it is simple. First, you must install a
Python 2 library called pypcapfile[3] - it provides a simple interface to load
and interact with a pcap file. Running `sudo pip2 install pypcapfile` will
install it (tested on Ubuntu 16.04 LTS and Arch Linux). The script has no
other external dependencies.

To run the script, use Python 2:
python2 btle-parse.py <path-to-pcap-file>

Running it with no argument, or more than one argument, will print a helpful
error message.

Note: running btle-parse.py with capture.pcap will error out, since it doesn't
have the 24-byte PPI header that Mike Ryan's pcap files have. I didn't feel like
fixing it, since capture.pcap contains encrypted data and it wouldn't give any
useful or easily verifiable results.

[1] https://github.com/adafruit/Adafruit_BLESniffer_Python
[2] https://lacklustre.net/bluetooth/crackle-sample.tgz
[3] https://pypi.python.org/pypi/pypcapfile
