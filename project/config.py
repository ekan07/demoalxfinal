""" App Configuration file """

# Global config object: DEBUG, TESTING are among default built-in configuration variables
class Config(object):
    DEBUG = False
    TESTING = False

    # Create a set of allowed extensions
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
    # Set a max and min filesize limit for images
    MAX_IMAGE_FILESIZE = 2 * 1024 * 1024
    # MIN_IMAGE_FILESIZE = 2 * 1024 * 1024

    # The absolute path of the directory containing CSV files for users to download
    # CLIENT_CSV = "/home/ubuntu/project/studentrecord/static/client/csv"
    CLIENT_CSV = "/home/ekan07/cs50finalproject/project/studentrecord/static/client/csv"

# The config class we'll use for running in production.
class ProductionConfig(Config):
    pass

# The config class we'll use for development
class DevelopmentConfig(Config):
    DEBUG = True

    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Create a set of allowed extensions
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]

    # Set a max and min filesize limit for images
    MAX_IMAGE_FILESIZE = 2 * 1024 * 1024
    # MIN_IMAGE_FILESIZE = 2 * 1024 * 1024

    # The absolute path of the directory containing CSV files for users to download
    # CLIENT_CSV = "/home/ubuntu/project/studentrecord/static/client/csv"
    CLIENT_CSV = "/home/ekan07/cs50finalproject/project/studentrecord/static/client/csv"

# The class we'll use for testing
class TestingConfig(Config):
    TESTING = True
