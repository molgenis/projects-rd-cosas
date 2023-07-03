
import requests

class Cartagenia:
  """Cartagenia Client"""
  def __init__(self, url, token):
    self.session = requests.Session()
    self._api_url = url
    self._api_token = token 
    self._headers = {'x-api-key': self._api_token}

  def getData(self):
    response = self.session.get(url=self._api_url, headers=self._headers)
    response.raise_for_status()
    data = response.json()
    if 'Output' not in data:
      raise KeyError('Expected object "Output" not found')
    return list(eval(data['Output']))