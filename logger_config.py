import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='security_log.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#this gives a logging blueprint for every file in the project