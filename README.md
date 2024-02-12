# Asterisk Multicast Paging Repeater

For compatibility with FreePBX, use the Python 3.6 virtual environment

### Configuration

In _config.py_:
```
asterisk_multicast_address = '224.0.1.116'
asterisk_multicast_port = 5001

poly_multicast_address = '224.0.1.116'
poly_multicast_port = 7659  # DTMF 'poly'
poly_multicast_ttl = 32

poly_group = 26
poly_sender_id = 'Asterisk'
```

### Poly XML Configuration
Minimum example settings to receive group page (group 1 is page group 26 above (25 + 1))
```
ptt.address="224.0.1.116"
ptt.port="7659"
ptt.pageMode.enable="1"
ptt.pageMode.group.1.available="1"
ptt.pageMode.group.1.allowReceive="1"
ptt.pageMode.group.1.subscribed"1"
```
SpectraLink PTT uses ports 5001 to 5025 mapped to the channels 1 to 25.

**Note: Changing Poly Paging multicast address or port requires a reboot of the phone,
even though the web UI does not indicate a reboot is necessary to apply the settings**

© Copyright 2024 Stuart Wyatt

This project is licensed under the terms of the [MIT license](LICENSE).