import logging

# Create a logger
logger = logging.getLogger('token size status')
logger.setLevel(logging.INFO)

# Create a console handler and set the logging level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a logging format
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# # Add the formatter to the handler
# console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# OPTIONAL: If you want to log to a file
file_handler = logging.FileHandler('bot_logs.log')
file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
