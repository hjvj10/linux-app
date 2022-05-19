# Proton VPN Linux App

Copyright (c) 2021 Proton Technologies AG

This repository holds the Proton VPN Linux App.
For licensing information see [COPYING](COPYING.md).
For contribution policy see [CONTRIBUTING](CONTRIBUTING.md).

## Description
The [Proton VPN](https://protonvpn.com) Linux App Library is intended for every Proton VPN service user.

You can download the latest stable release, either from our official repositories or directly on the [official GitHub repository](https://github.com/ProtonVPN/linux-app/releases/latest).

### Dependencies:
| **Distro**                              | **Command**                                                                                                     |
|:----------------------------------------|:----------------------------------------------------------------------------------------------------------------|
|Fedora/CentOS/RHEL                       | `python3-gi, python3-gi-cairo, python3-psutil` |
|Ubuntu/Linux Mint/Debian and derivatives | `gtk3, python3-gobject, python3-psutil` |
|Arch Linux/Manjaro                       | `gtk3, python-gobject, python-psutil` |

### Indicator/Tray dependency
| **Distro**                              | **Command**                                                                                                     |
|:----------------------------------------|:----------------------------------------------------------------------------------------------------------------|
|Fedora/CentOS/RHEL                       | `libappindicator-gtk3` |
|Ubuntu/Linux Mint/Debian and derivatives | `gir1.2-appindicator3-0.1` |
|Arch Linux/Manjaro                       | `libappindicator-gtk3` |

### Additional dependency:
[Proton VPN NM Library](https://github.com/ProtonVPN/protonvpn-nm-lib)

## Installation
Follow our [knowledge base article](https://protonvpn.com/support/official-linux-client/) on how to install the Proton VPN Linux App on your system.
