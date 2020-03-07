# homeassistant-helios

[![Buy me a smoothie](https://img.shields.io/badge/Buy%20me%20a-smoothie-blue?style=for-the-badge&logo=PAYPAL)](https://www.paypal.me/asev)

Custom component for Home Assistant to connect Helios ventilation system.

Tested on Helios KWL EC 300 W. Most of functions will work on other Helios devices.

![Example screenshot](screenshot.png)

## Installation

1. Make sure your Helios is connected to local network and you know it's IP address.
2. Copy the custom_components folder to your own Home Assistant /config folder.
3. Enable the component by adding the following in your `configuration.yml`:
```yaml
helios:
    host: IP_ADDRESS_OF_HELIOS_DEVICE
```
4. Restart Home Assistant server

## Configuration

- `next_filter_change` (optional) configuration variable with date of next filter change.
It can be used to setup automated reminder for filter change.
```yaml
helios:
    host: !secret ip_helios
    next_filter_change: "2020-08-08"
```

## Feedback

Your feedback or pull requests or any other contribution is welcome. Please let me know how it works on other Helios models.