import os
import yaml
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Config:
    _instance = None
    _config = {}
    _config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from YAML files."""
        try:
            # Load logging configuration
            logging_config_path = os.path.join(self._config_dir, 'logging.yaml')
            with open(logging_config_path, 'r') as f:
                logging_config = yaml.safe_load(f)
                self._config['logging'] = logging_config

            # Load application settings
            settings_config_path = os.path.join(self._config_dir, 'settings.yaml')
            with open(settings_config_path, 'r') as f:
                settings_config = yaml.safe_load(f)
                self._config['settings'] = settings_config

            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section (str): Configuration section name
            key (str, optional): Configuration key name
            default (Any, optional): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        try:
            if key is None:
                return self._config.get(section, default)
            return self._config.get(section, {}).get(key, default)
        except Exception as e:
            logger.error(f"Error getting configuration value: {str(e)}")
            return default

    def get_scraping_config(self) -> Dict:
        """Get scraping configuration."""
        return self.get('settings', 'scraping', {})

    def get_options_config(self) -> Dict:
        """Get options configuration."""
        return self.get('settings', 'options', {})

    def get_risk_config(self) -> Dict:
        """Get risk management configuration."""
        return self.get('settings', 'risk', {})

    def get_strategy_config(self) -> Dict:
        """Get strategy configuration."""
        return self.get('settings', 'strategy', {})

    def get_sentiment_config(self) -> Dict:
        """Get sentiment analysis configuration."""
        return self.get('settings', 'sentiment', {})

    def get_storage_config(self) -> Dict:
        """Get storage configuration."""
        return self.get('settings', 'storage', {})

    def get_api_config(self) -> Dict:
        """Get API configuration."""
        return self.get('settings', 'api', {})

    def get_logging_config(self) -> Dict:
        """Get logging configuration."""
        return self.get('logging', {}) 