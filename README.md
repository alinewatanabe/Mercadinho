# Mercadinho - RFID Point of Sale System

## Overview

Mercadinho is a desktop-based Point of Sale (POS) system designed for small markets and retail stores. It features integrated RFID technology for fast and efficient product checkout, comprehensive inventory management, and customer registration capabilities. Built with PyQt5, it provides an intuitive graphical interface for seamless retail operations.

## Features

- **RFID-Based Checkout**: Instantly read product information using RFID technology for quick transactions
- **Customer Management**: Register and manage customer information with CPF and phone number storage
- **Inventory Management**: Track product stock levels, manage product information, and receive real-time inventory updates
- **Self-Checkout**: Enable customers to scan items independently during checkout
- **Secure Database**: SQLite database backend for reliable data persistence
- **Multi-Window Interface**: Organized UI with separate screens for home, registration, inventory, and checkout

## Technologies

- **Framework**: PyQt5 - Modern GUI framework for desktop applications
- **Database**: SQLite3 - Lightweight, file-based database
- **RFID Reader**: MFRC522 - Contactless RFID card reader support
- **Data Processing**: Pandas, NumPy - Data analysis and manipulation
- **Communication**: PySerial - Serial port communication for hardware devices

## Installation

### Prerequisites
- Python 3.8 or higher
- RFID Reader (MFRC522 compatible)
- Serial connection capability for hardware communication

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/alinewatanabe/Mercadinho.git
   cd Mercadinho
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python Python_Files/main.py
   ```

## Project Structure

| Directory/File | Purpose |
|---|---|
| **Python_Files/** | Core application modules and logic |
| main.py | Application entry point and main window controller |
| database.py | SQLite database operations and queries |
| home.py | Home screen interface and navigation |
| register.py | Customer registration module |
| inventory.py | Inventory management and product tracking |
| self_checkout.py | Self-checkout interface for customers |
| stand_by.py | Standby/screensaver display screen |
| RFID.py | RFID reader thread and communication |
| **UI_Files/** | Qt Designer UI definition files (.ui) |
| **icons/** | Application icons and resources (.qrc) |
| **Doc_Files/** | Documentation, presentations, and media assets |
| **requirements.txt** | Python package dependencies and versions |
| **README.md** | Project documentation |

## Usage

1. **Launch the Application**: Run `main.py` to start the POS system
2. **Home Screen**: Choose between Customer Registration or Checkout
3. **Customer Registration**: Register new customers or existing customers login
4. **Checkout Process**: Use RFID scanner to select items and complete purchase
5. **Inventory Management**: Access the inventory screen to manage product catalog

## Hardware Requirements

- RFID Reader: MFRC522-compatible reader
- Serial Port: For RFID reader communication
- Display: Minimum 1024x768 resolution recommended

## Contact
For questions or support, please contact the project maintainer:
- **Email**: [linenwatanabe@gmail.com](mailto:linenwatanabe@gmail.com)
- **GitHub**: [alinewatanabe](https://github.com/alinewatanabe)

---

**Note**: This is a desktop application designed for local retail operations. For online marketplace functionality, please refer to alternative solutions.
