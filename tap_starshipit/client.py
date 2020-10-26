import backoff
import requests
from requests.exceptions import ConnectionError
from singer import metrics

class Server5xxError(Exception):
    pass

class APIClient(object):
    def __init__(self, config, config_path):
        self.__config_path = config_path
        self.__config = config
        self.__api_key = config.get('api_key')
        self.__subscription_key = config.get('subscription_key')
        self.__session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__session.close()

    @backoff.on_exception(backoff.expo,
                          (Server5xxError, ConnectionError),
                          max_tries=5,
                          factor=2)
    def request(self, method, path=None, **kwargs):

        url = f'https://api.starshipit.com/api/{path}'

        if 'endpoint' in kwargs:
            endpoint = kwargs['endpoint']
            del kwargs['endpoint']
        else:
            endpoint = None

        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        kwargs['headers']['StarShipIT-Api-Key'] = self.__api_key
        kwargs['headers']['Ocp-Apim-Subscription-Key'] = self.__subscription_key

        with metrics.http_request_timer(path) as timer:
            response = self.__session.request(method, url, **kwargs)
            timer.tags[metrics.Tag.http_status_code] = response.status_code

        if response.status_code >= 500:
            raise Server5xxError()

        response.raise_for_status()

        return response.json()

    def get(self, path, **kwargs):
        return self.request('GET', path=path, **kwargs)

    def post(self, path, **kwargs):
        return self.request('POST', path=path, **kwargs)
