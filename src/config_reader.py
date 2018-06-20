"""Small module used for abstracting configuration reads."""
class ConfigReader: # pylint: disable=too-few-public-methods
    """
    This small helper class reads a specified config file and returns the
    requested attribute values.
    """
    def __init__(self, path='config/initial.config'):
        """
        :param path: config file which should be read
        :raises FileNotFoundError: if the config file does not exist
        """
        self.path = path

        # Opening the file to check whether it exists
        file = open(self.path)
        file.close()

    def get_attr(self, attr):
        """
        Returns the value of the specified attribute

        :param attr: e.g.: username
        :returns: value of attribute
        :raises FileNotFoundError: if the config file does not exist
        """
        with open(self.path) as file:
            content = file.read().splitlines()

        for line in content:
            if attr + '=' in line:
                return line.split(attr + '=')[1]
        return None

if __name__ == '__main__':
    CFG_RDR = ConfigReader()
    print(CFG_RDR.get_attr('username'))
    print(CFG_RDR.get_attr('backend_address'))
