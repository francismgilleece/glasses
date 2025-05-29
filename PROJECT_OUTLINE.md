# Wearable Companion Device Project Outline

## Project Overview
A modular wearable companion device that aggregates and displays information from multiple sources on a transparent OLED screen, designed for extensibility and real-time data processing.

## Hardware Architecture

### Current Components
- **Raspberry Pi Zero 2W**: Main processing unit
  - ARM Cortex-A53 quad-core 1GHz
  - 512MB RAM
  - WiFi 802.11 b/g/n, Bluetooth 4.2
  - GPIO pins for peripheral connections
  
- **128x64px Transparent OLED Display**: Primary output device
  - I2C/SPI communication interface
  - Monochrome display (consider color upgrade path)
  - Low power consumption for wearable use
  
- **Adafruit PowerBoost 500**: Power management
  - 5V boost from 3.7V LiPo battery
  - USB charging capability
  - Low battery indicator support

### Future Hardware Considerations
- **Camera Module**: Vision input for AR/object recognition
- **IMU/Accelerometer**: Motion detection and gesture controls
- **Microphone**: Voice commands and audio processing
- **Speaker/Haptic Feedback**: User notifications
- **Additional Sensors**: Temperature, light, proximity

## Software Architecture



### Core System (Python-based)

#### 1. Main Controller (`main.py`)
```
├── System initialization
├── Module loader and manager
├── Event loop coordinator
├── Power management integration
└── Error handling and recovery
```

#### 2. Display Manager (`display/`)
```
├── display_controller.py    # OLED interface and rendering
├── ui_renderer.py          # UI layout and graphics
├── screen_modes.py         # Different display modes/themes
└── font_manager.py         # Font handling for limited space
```

#### 3. Data Input Modules (`inputs/`)
```
├── base_input.py           # Abstract base class for all inputs
├── phone_connector.py      # Bluetooth/WiFi connection to phone
├── web_scraper.py          # Internet data fetching
├── llm_client.py           # Web LLM API integration
├── camera_input.py         # Future: Camera vision processing
├── voice_input.py          # Future: Voice command processing
└── sensor_input.py         # Future: Environmental sensors
```

#### 4. Data Processing (`processing/`)
```
├── data_aggregator.py      # Combines data from multiple sources
├── priority_manager.py     # Determines what to display when
├── text_processor.py       # Text summarization and formatting
├── image_processor.py      # Future: Image analysis and overlay
└── ml_inference.py         # Future: On-device ML processing
```

#### 5. Communication Layer (`communication/`)
```
├── bluetooth_manager.py    # BLE communication with phone
├── wifi_manager.py         # WiFi connectivity and management
├── api_client.py           # HTTP client for web services
└── protocol_handler.py     # Custom protocols for device communication
```

#### 6. Configuration & Storage (`config/`)
```
├── settings_manager.py     # User preferences and device settings
├── data_cache.py           # Local data storage and caching
├── user_profiles.py        # Multiple user support
└── device_calibration.py   # Hardware calibration settings
```

### Mobile App Integration (FUTURE)

#### Companion App Features
- **Device pairing and setup**
- **Data source configuration**
- **Custom notification rules**
- **Display preference settings**
- **Remote control interface**

#### Data Sources from Phone
- Notifications (calls, messages, apps)
- Calendar events and reminders
- Health data (steps, heart rate)
- Location and navigation
- Music/media controls

## Information Flow Architecture

### 1. Input Layer
```
[Phone] ←→ [Bluetooth/WiFi] ←→ [Pi Zero 2W]
[Internet APIs] ←→ [WiFi] ←→ [Pi Zero 2W]
[Web LLM] ←→ [HTTP/WebSocket] ←→ [Pi Zero 2W]
```

### 2. Processing Pipeline
```
Raw Data → Filtering → Prioritization → Formatting → Display Queue → OLED
```

### Key Libraries and Dependencies
- **Display**: `luma.oled`, `Pillow` (PIL)
- **Bluetooth**: `pybluez`, `bleak`
- **WiFi/Network**: `requests`, `aiohttp`, `websockets`
- **Data Processing**: `pandas`, `numpy` 
- **Configuration**: `pydantic`, `yaml`
- **Logging**: `structlog`
- **Testing**: `pytest`, `mock`

## Project Structure

```
glassesnew/
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   ├── default_settings.yaml
│   ├── device_config.yaml
│   └── user_preferences.yaml
├── src/
│   ├── main.py
│   ├── display/
│   ├── inputs/
│   ├── processing/
│   ├── communication/
│   ├── config/
│   └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── hardware/
├── docs/
│   ├── hardware_setup.md
│   ├── api_documentation.md
│   └── user_guide.md
├── scripts/
│   ├── install.sh
│   ├── start_service.sh
│   └── update_system.sh
├── mobile_app/
│   ├── android/
│   └── ios/
└── assets/
    ├── fonts/
    ├── icons/
    └── templates/
```

## Development Timeline (Week, Day)

1,1: Create outline page and outline framework for device plan. Order components.
1,2: Categorize and localize dependencies for each package: eg processing, inputs, network. Set up information flow architecture. Create display manager module. 

