# 🎮 Gaming Mouse Control Center - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (for full functionality)
- Administrative privileges (for USB device access)

### Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd Mouse-tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📦 Dependencies

### Required Libraries
- **PyQt6** - Modern GUI framework
- **hidapi** - HID device communication
- **pyusb** - USB device access
- **pywin32** - Windows API access
- **psutil** - System information
- **pynput** - Input device monitoring
- **requests** - Web requests
- **beautifulsoup4** - Web scraping

### Installation Commands
```bash
pip install PyQt6 hidapi pyusb pywin32 psutil pynput requests beautifulsoup4 libusb-package
```

## 🔧 Configuration

### Device Permissions

**Windows:**
1. Run as Administrator for full USB access
2. Or install USB drivers manually:
   ```bash
   # Install libusb drivers
   pip install libusb-package
   ```

### Troubleshooting Common Issues

**Device not detected:**
1. Close manufacturer software (Razer Synapse, Logitech G HUB, etc.)
2. Run as Administrator
3. Check USB connection
4. Install missing dependencies

**Permission errors:**
```bash
# Install Windows API support
pip install pywin32

# Run as Administrator
python main.py
```

**Library errors:**
```bash
# Install all required libraries
pip install -r requirements.txt

# Check library status in the app's Diagnostics tab
```

## 🖱️ Supported Devices

### Supported Brands
- **Razer** - Full protocol support
- **Logitech** - G-series mice
- **SteelSeries** - Rival series
- **CyberpowerPC** - Gaming mice
- **iBuyPower** - Gaming mice
- **ASUS, ROCCAT, Glorious** - Basic support

### Device Compatibility
- Gaming mice with HID/USB support
- Wireless and wired mice
- Mice with RGB lighting
- Mice with programmable buttons

## 🎯 Features

### Core Features
- **Device Detection** - Automatic mouse detection and identification
- **Multi-Protocol Support** - Custom protocols for each manufacturer
- **Robust Connection** - Multiple connection methods with fallback
- **Settings Management** - Save/load profiles and configurations

### Advanced Features
- **Macro Recording** - Record and playback mouse actions
- **Real-time Tracking** - Monitor mouse movement and statistics
- **Game Detection** - Automatic profile switching for games
- **RGB Control** - Advanced lighting effects and animations
- **Battery Monitoring** - Wireless mouse battery status
- **Firmware Updates** - Automatic firmware detection and updates

### Diagnostics
- **System Information** - Complete system and library status
- **Device Testing** - Comprehensive device connection testing
- **Performance Monitoring** - Real-time system performance
- **Debug Tools** - Advanced troubleshooting information

## 📁 Project Structure

```
Mouse-tool/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── SETUP.md              # Setup guide (this file)
└── mouse_config/          # Main package
    ├── __init__.py
    ├── core/              # Core systems
    │   ├── protocols.py   # Device communication
    │   ├── detection.py   # Mouse detection
    │   ├── controller.py  # Device control
    │   └── settings.py    # Settings management
    ├── advanced/          # Advanced features
    │   ├── macros.py      # Macro recording
    │   ├── tracking.py    # Mouse tracking
    │   ├── games.py       # Game detection
    │   ├── rgb.py         # RGB effects
    │   └── battery.py     # Battery monitoring
    ├── firmware/          # Firmware management
    │   ├── downloader.py  # Firmware download
    │   ├── scraper.py     # Firmware scraping
    │   └── flasher.py     # Firmware flashing
    ├── gui/               # User interface
    │   ├── main_window.py # Main window
    │   ├── tabs/          # Tab widgets
    │   ├── widgets/       # Custom widgets
    │   └── styles/        # UI themes
    └── utils/             # Utilities
        ├── logger.py      # Logging system
        ├── config.py      # Configuration
        └── helpers.py     # Helper functions
```

## 🎮 Usage Guide

### Basic Setup
1. Connect your gaming mouse
2. Launch the application
3. Click "🔄 Scan" to detect your device
4. Select your mouse from the dropdown
5. Configure settings in the various tabs

### Advanced Features

**Macros:**
- Click "🔴 Record Macro" to start recording
- Perform mouse actions
- Click "⏹️ Stop" to finish
- Click "▶️ Play" to playback

**Statistics:**
- Click "▶️ Start Tracking" to monitor usage
- View real-time statistics
- Export tracking data

**Profiles:**
- Create game-specific profiles
- Automatic profile switching
- Save/load configurations

**Firmware:**
- Check for updates automatically
- Download firmware safely
- Follow on-screen instructions

## 🔒 Security Notes

### Network Access
- Firmware downloads require internet access
- Web scraping for manufacturer sites
- No data is sent to external servers

### System Access
- USB device access requires permissions
- Windows API access for advanced features
- All access is logged and monitored

## 🐛 Troubleshooting

### Common Solutions

**"No devices found"**
1. Check USB connection
2. Close manufacturer software
3. Run as Administrator
4. Install missing dependencies

**"Connection failed"**
1. Try different USB ports
2. Update device drivers
3. Check device compatibility
4. Use Debug dialog for details

**"Library errors"**
1. Install missing packages
2. Update Python to 3.8+
3. Check 32-bit vs 64-bit compatibility

### Getting Help

1. **Debug Dialog** - Click "🔧 Debug" for detailed information
2. **Logs** - Check `.mouse_config/logs/` for detailed logs
3. **System Info** - Diagnostics tab shows system status
4. **Documentation** - Check README.md for detailed info

## 📱 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11
- **Python**: 3.8+
- **RAM**: 4GB+
- **Storage**: 100MB free space
- **USB**: Available USB port

### Recommended Requirements
- **OS**: Windows 11
- **Python**: 3.10+
- **RAM**: 8GB+
- **Storage**: 500MB free space
- **USB**: USB 3.0 port

## 🔄 Updates

### Application Updates
- Check for updates in the app
- Download latest version from repository
- Backup settings before updating

### Firmware Updates
- Automatic detection in Firmware tab
- Safe download and installation
- Follow on-screen instructions carefully

## 📞 Support

### Getting Help
1. Check the Troubleshooting section
2. Use the Debug dialog for diagnostics
3. Review application logs
4. Check GitHub issues

### Reporting Issues
Include:
- Operating system version
- Python version
- Mouse model and manufacturer
- Error messages and logs
- Steps to reproduce

---

**Enjoy your enhanced gaming mouse experience! 🎮**
