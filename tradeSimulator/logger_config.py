import logging
from tradeSimulator.config import Config

def setup_logging():
    """Set up logging configuration dynamically."""
    logger = logging.getLogger()
    logger.setLevel(Config.get_log_level())  # Use the dynamic method to fetch log level

    # Configure logging format
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(threadName)s] %(name)s - %(funcName)s:%(lineno)d %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
