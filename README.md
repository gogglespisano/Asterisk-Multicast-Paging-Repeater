# Asterisk Multicast Paging Repeater

### Configuration

In _config.py_:
```
asterisk_multicast_address = '224.0.1.116'
asterisk_multicast_port = 5001

poly_multicast_address = '224.0.1.116'
poly_multicast_port = 5002
poly_multicast_ttl = 32

poly_group = 26
poly_sender_id = 'Asterisk'
```

**Note: Changing Poly Paging multicast address or port requires a reboot of the phone,
even though the web UI does not indicate a reboot is necessary to apply the settings**

© Copyright 2024 Stuart Wyatt - All rights reserved.
This project is licensed under the terms of the [MIT license](LICENSE).