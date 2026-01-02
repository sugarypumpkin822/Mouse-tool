# 🎮 Gaming Mouse Control Center - Pro Edition

A comprehensive, professional-grade mouse configuration tool with advanced features for gaming mice from multiple manufacturers.

## ✨ Features

### 🖱️ Device Support
- **Multiple Brands**: Razer, Logitech, SteelSeries, CyberpowerPC, iBuyPower, ASUS, ROCCAT, and more
- **Advanced Protocols**: Custom protocols for each manufacturer with full feature support
- **Robust Connection**: Multiple connection methods with automatic fallback and error recovery
- **Firmware Updates**: Automatic firmware detection and update system

### 🎬 Macro System
- **Recording**: Record mouse movements and clicks with precise timing
- **Playback**: Play back macros with configurable repeat counts
- **Button Remapping**: Full button remapping with custom actions
- **Advanced Actions**: DPI switching, profile changes, macro triggers

### 📊 Real-time Analytics
- **Movement Tracking**: Track total distance, speed, and acceleration
- **Click Statistics**: Monitor click frequency, patterns, and CPM
- **Session Analytics**: Detailed session statistics and performance metrics
- **Battery Monitoring**: Wireless mouse battery level and estimated time

### 🎮 Smart Features
- **Game Detection**: Automatic game detection and profile switching
- **RGB Control**: Advanced RGB effects with custom animations
- **Profile Management**: Multiple profiles with automatic switching
- **Cloud Sync**: Settings synchronization (coming soon)

### 🔧 Diagnostics
- **System Info**: Complete system and library status
- **Device Testing**: Comprehensive device connection testing
- **Performance Monitor**: Real-time performance monitoring
- **Debug Tools**: Advanced debugging and troubleshooting

## 📁 Project Structure

```
Mouse-tool/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── mouse_config/          # Main package directory
│   ├── __init__.py
│   ├── core/              # Core systems
│   │   ├── __init__.py
│   │   ├── protocols.py   # Device communication protocols
│   │   ├── detection.py   # Mouse detection and identification
│   │   ├── controller.py  # Device control and management
│   │   └── settings.py    # Settings and profile management
│   ├── advanced/          # Advanced features
│   │   ├── __init__.py
│   │   ├── macros.py      # Macro recording and playback
│   │   ├── tracking.py    # Mouse movement tracking
│   │   ├── games.py       # Game detection and profiles
│   │   ├── rgb.py         # RGB effects and animations
│   │   └── battery.py     # Battery monitoring
│   ├── firmware/          # Firmware management
│   │   ├── __init__.py
│   │   ├── downloader.py  # Firmware download system
│   │   ├── scraper.py     # Firmware web scraper
│   │   └── flasher.py     # Firmware flashing utilities
│   ├── gui/               # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py # Main application window
│   │   ├── tabs/          # Tab widgets
│   │   │   ├── __init__.py
│   │   │   ├── performance.py
│   │   │   ├── lighting.py
│   │   │   ├── advanced.py
│   │   │   ├── profiles.py
│   │   │   ├── firmware.py
│   │   │   ├── macros.py
│   │   │   ├── statistics.py
│   │   │   └── diagnostics.py
│   │   ├── widgets/       # Custom widgets
│   │   │   ├── __init__.py
│   │   │   ├── lcd_display.py
│   │   │   ├── color_picker.py
│   │   │   └── progress_bar.py
│   │   └── styles/        # UI styles and themes
│   │       ├── __init__.py
│   │       └── modern.py
│   └── utils/             # Utilities
│       ├── __init__.py
│       ├── logger.py      # Logging system
│       ├── config.py      # Configuration management
│       └── helpers.py     # Helper functions
└── tests/                 # Unit tests (optional)
    ├── __init__.py
    ├── test_protocols.py
    ├── test_detection.py
    └── test_macros.py
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (for full functionality)
- Administrative privileges (for USB device access)

### Setup
1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### Dependencies
- **PyQt6**: Modern GUI framework
- **hidapi**: HID device communication
- **pyusb**: USB device access
- **pywin32**: Windows API access
- **psutil**: System information
- **pynput**: Input device monitoring
- **requests**: Web requests
- **beautifulsoup4**: Web scraping

## 🎯 Usage

### Basic Setup
1. Connect your gaming mouse
2. Click "🔄 Scan" to detect your device
3. Select your mouse from the dropdown
4. Configure settings in the various tabs

### Advanced Features
- **Macros**: Record and playback complex mouse sequences
- **Tracking**: Monitor your mouse usage patterns
- **Profiles**: Create game-specific profiles
- **Diagnostics**: Troubleshoot connection issues

## 🔧 Troubleshooting

### Common Issues
1. **Device not detected**: 
   - Check USB connection
   - Close manufacturer software
   - Run as administrator

2. **Permission errors**:
   - Install pywin32: `pip install pywin32`
   - Run as administrator

3. **Library errors**:
   - Install all dependencies from requirements.txt
   - Check Python version compatibility

### Debug Mode
Click the "🔧 Debug" button for detailed device information and troubleshooting steps.

## 🛠️ Development

### Architecture
The application follows a modular architecture with clear separation of concerns:
- **Core**: Device communication and control
- **Advanced**: High-level features and automation
- **GUI**: User interface components
- **Utils**: Shared utilities and helpers

### Adding New Devices
1. Add vendor/product IDs to `detection.py`
2. Implement protocol in `protocols.py`
3. Add UI support in relevant tabs

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is released under the MIT License. See LICENSE file for details.

## 🤝 Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the debug information

## 🔄 Updates

The tool automatically checks for firmware updates and can download/install them when available.

---

**Note**: This tool is not affiliated with any mouse manufacturer. Use at your own risk.
