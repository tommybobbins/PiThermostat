#!/usr/bin/python3
import configparser
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def get_config_path():
    """Get the path to the configuration file"""
    # Try system config first
    system_config = Path('/etc/pithermostat.conf')
    if system_config.exists():
        return str(system_config)
    
    # Fall back to local config
    local_config = Path(__file__).parent.parent / 'etc' / 'pithermostat.conf'
    if local_config.exists():
        return str(local_config)
    
    raise FileNotFoundError("Could not find pithermostat.conf in /etc/ or project etc/ directory")

def setup_logging():
    """Setup logging configuration"""
    # Read configuration
    parser = configparser.ConfigParser()
    config_path = get_config_path()
    parser.read(config_path)
    debug = parser.get('main', 'debug')
    DEBUG = {'True': True, 'False': False}.get(debug, False)

    # Configure logging
    logger = logging.getLogger('pithermostat')
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

    # Create handlers
    console_handler = logging.StreamHandler()
    
    # Ensure log directory exists
    log_dir = Path('/var/log')
    if not log_dir.exists():
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'pithermostat.log'
    file_handler = RotatingFileHandler(str(log_file), maxBytes=1048576, backupCount=5)

    # Set log levels
    console_handler.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    file_handler.setLevel(logging.DEBUG if DEBUG else logging.INFO)

    # Create formatters and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger, DEBUG

# Initialize logging
logger, DEBUG = setup_logging()

def debug_log(message):
    """Log a debug message if debug mode is enabled"""
    if DEBUG:
        logger.debug(message)

def info_log(message):
    """Log an info message"""
    logger.info(message)

def error_log(message):
    """Log an error message"""
    logger.error(message)

def warning_log(message):
    """Log a warning message"""
    logger.warning(message) 