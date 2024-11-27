import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='security_log.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)