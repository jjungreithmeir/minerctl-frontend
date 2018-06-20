"""Small module used for abstracting configuration reads."""
import configparser

class ConfigReader: # pylint: disable=too-few-public-methods
    """
    This small helper class reads a specified config file and returns the
    requested attribute values.
    """
    def __init__(self, path='config/minerctl.ini'):
        """
        :param path: config file which should be read
        :raises FileNotFoundError: if the config file does not exist
        """
        self.path = path
        self.config = configparser.ConfigParser()
        cfg = self.config.read(self.path)

        if not cfg:
            raise FileNotFoundError


    def get_attr(self, attr):
        """
        Returns the value of the specified attribute.

        :param attr: e.g.: username
        :returns: value of attribute
        :raises FileNotFoundError: if the config file does not exist
        """
        return self.config['Initial Setup'][attr]

    def write_attr(self, attr, value):
        """
        Writes the value to the specified attribute.

        :param attr: e.g.: username
        :param value: e.g.: admin@mail.com
        :raises FileNotFoundError: if the config file does not exist
        """
        self.config[attr] = value

if __name__ == '__main__':
    CFG_RDR = ConfigReader()
    print(CFG_RDR.get_attr('username'))
    print(CFG_RDR.get_attr('backend_address'))
