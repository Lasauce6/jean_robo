import collections
import inspect
import json
import operator
import sys

import os


def get(iterable, **attrs):
    """Helper function to perform lookups in collections."""
    if isinstance(iterable, dict):
        for key, elem in iterable.items():
            if all(operator.attrgetter(attr)(elem) == value for attr, value in attrs.items()):
                return key, elem
        return None, None

    for elem in iterable:
        if all(operator.attrgetter(attr)(elem) == value for attr, value in attrs.items()):
            return elem
    return None


class globalConfig:
    def __init__(self, file):

        global cfg

        try:
            with open(file, 'r') as jsonfile:
                cfg = json.load(jsonfile)
        except Exception as e:
            print(e)
            input("Press any key to exit the program")
            sys.exit()

        if not cfg['config']['connection']['Google API key']:
            input('Error: Missing Youtube API v3 key in config file!')
            sys.exit()

        if not cfg['config']['connection']['Twitch app id']:
            input('ERROR: Missing Twitch app id in config file!')
            sys.exit()

        if not cfg['config']['connection']['Twitch secret app id']:
            input('ERROR: Missing Twitch secret app id in config file!')
            sys.exit()

        if self.getYouTubersNr() == 0:
            input('ERROR: No YouTubers found in config file list or missing information!')
            sys.exit()

        if self.getStreamerNr() == 0:
            input('ERROR: No Streamers found in config file list or missing information!')
            sys.exit()

    def getConnectionData(self):
        return [cfg['config']['connection']['Google API key'],
                cfg['config']['connection']['Twitch app id'],
                cfg['config']['connection']['Twitch secret app id']]

    def getPingTime(self):
        return cfg['config']['main']['Ping Every x Minutes']

    def getYouTubersList(self):
        return cfg['config']['YouTubers']

    def getStreamerList(self):
        return cfg['config']['Streamers']

    def getYoutuberDiscordChannelList(self, youtuber):
        return youtuber['Discord Channel']

    def getStreamerDiscordChannelList(self, streamer):
        return streamer['Discord Channel']

    def getYoutuberDiscordChannelNr(self, youtuber):
        if not youtuber['Discord Channel']:
            return 0
        return len(youtuber['Discord Channel'])

    def getStreamerDiscordChannelNr(self, streamer):
        if not streamer['Discord Channel']:
            return 0
        return len(streamer['Discord Channel'])

    def getYouTubersNr(self):
        if not cfg['config']['YouTubers']:
            return 0
        return len(cfg['config']['YouTubers'])

    def getStreamerNr(self):
        if not cfg['config']['Streamers']:
            return 0
        return len(cfg['config']['Streamers'])


class Config:
    """The config object, created from a json file."""

    def __init__(self, file, **options):

        super().__setattr__('_data', {})
        self.file = file
        self.encoding = options.pop('encoding', None)
        self.object_hook = options.pop('object_hook', _ConfigDecoder().decode)
        self.encoder = options.pop('encoder', _ConfigEncoder)

        with open(self.file, 'r', encoding=self.encoding) as fp:
            self._data = json.load(fp, object_pairs_hook=self.object_hook)

    def save(self):
        """Saves the config on disk."""
        tmp_file = self.file + '~'
        with open(tmp_file, 'w', encoding=self.encoding) as fp:
            json.dump(self._data, fp, ensure_ascii=True, cls=self.encoder)
        os.replace(tmp_file, self.file)

    # utility

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __getattr__(self, item, default=None):
        return getattr(self._data, item, default)

    def __setattr__(self, key, value):
        if key in self._data:
            setattr(self._data, key, value)
        else:
            super().__setattr__(key, value)


class ConfigElement(collections.Mapping):
    """The main data holding class."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__)


class _ConfigEncoder(json.JSONEncoder):
    """Custom JSON encoder."""

    def default(self, o):
        """Support of ConfigElement's serialization."""
        if isinstance(o, ConfigElement):
            # Ignore 'private' attributes
            for k in o.__dict__.copy():
                if k[0] == '_':
                    del o.__dict__[k]

            o.__dict__['__class__'] = o.__class__.__qualname__
            return o.__dict__

        # Let the base class default method raise the TypeError
        return super().default(self, o)


class _ConfigDecoder:
    """Custom JSON decoder.

    Do not instantiate as the inspect magic involved is not tailored for it.
    """

    def __init__(self):
        # Back once to reach Config.__init__
        # Back twice to reach the caller
        self._globals = inspect.currentframe().f_back.f_back.f_globals

    def decode(self, o):
        """Support the deserialization of ConfigElements objects."""
        o = collections.OrderedDict(o)
        if '__class__' in o:
            name = o.pop('__class__')

            # Check the general case
            if name == ConfigElement.__qualname__:
                return ConfigElement(**o)

            # Go look for a subclass in the caller's module
            parts = name.split('.')
            try:
                obj = self._globals[parts[0]]

                for part in parts[1:]:
                    if inspect.isclass(obj):
                        obj = obj.__dict__[part]
                    else:
                        raise TypeError('Expected class name.')
            except KeyError:
                raise KeyError(f'Could not find class {name} in {self._globals["__file__"]}')

            return obj(**o)

        # Try to convert keys to ints when possible
        for k, v in o.copy().items():
            try:
                o[int(k)] = v
            except ValueError:
                pass
            else:
                del o[k]
        return o
