""" App Configuration file """

import os


class Config(object):
    """
    Global config object: DEBUG, TESTING are among default built-in configuration variables
    """

    DEBUG = False
    TESTING = False

    # Create a set of allowed extensions
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
    # Set a max and min filesize limit for images
    MAX_IMAGE_FILESIZE = 2 * 1024 * 1024
    # MIN_IMAGE_FILESIZE = 2 * 1024 * 1024

    # The absolute path of the directory containing CSV files for users to download
    # i.e "/home/ekan07/alx-repos/demoalxfinal/project/"
    CLIENT_CSV = os.path.dirname(os.path.abspath(__file__))


class ProductionConfig(Config):
    """
    The config class we'll use to run in production environment.
    """
    pass


class DevelopmentConfig(Config):
    """
    The config class we'll use to run in development environment
    """

    DEBUG = True
    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True
    # Create a set of allowed extensions
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
    # Set a max and min filesize limit for images
    MAX_IMAGE_FILESIZE = 2 * 1024 * 1024
    # MIN_IMAGE_FILESIZE = 2 * 1024 * 1024

    # The absolute path of the directory containing CSV files for users to download
    # i.e "/home/ekan07/alx-repos/demoalxfinal/project/"
    CLIENT_CSV = os.path.dirname(os.path.abspath(__file__))


class TestingConfig(Config):
    """
    The class we'll use for testing
    """
    TESTING = True
