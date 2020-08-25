from ..authorization.authorization_api import AuthorizationApi
from ..common.common_funcs import CommonFuncs
import requests
import json
import logging


class HierarchiesApi():
    def __init__(
        self,
        application_name: str,
        environment_id: str, 
        authorization_api: AuthorizationApi,
        common_funcs: CommonFuncs,
        ):

        self._applicationName = application_name
        self.environmentId = environment_id
        self.authorization_api = authorization_api
        self.common_funcs = common_funcs

    def getHierarchies(self):
        """Gets all hierarchies from the specified TSI environment.

        Returns:
            dict: The hierarchies in form of the response from the TSI api call.
            Contains hierarchy id, names and source fields per hierarchy.

        Example:
            >>> from TSIClient import TSIClient as tsi
            >>> client = tsi.TSIClient()
            >>> hierarchies = client.getHierarchies()
        """

        authorizationToken = self.authorization_api._getToken()

        url = "https://" + self.environmentId + ".env.timeseries.azure.com/timeseries/hierarchies"
        querystring = self.common_funcs._getQueryString()
        payload = ""
        headers = {
            'x-ms-client-application-name': self._applicationName,
            'Authorization': authorizationToken,
            'Content-Type': "application/json",
            'cache-control': "no-cache",
        }

        try:
            response = requests.request(
                "GET",
                url,
                data=payload,
                headers=headers,
                params=querystring,
                timeout=10
            )
            response.raise_for_status()
            if response.text:
                jsonResponse = json.loads(response.text)
            
            result = jsonResponse
        
            while 'continuationToken' in list(jsonResponse.keys()):
                headers = {
                    'x-ms-client-application-name': self._applicationName,
                    'Authorization': authorizationToken,
                    'x-ms-continuation' : jsonResponse['continuationToken'],
                    'Content-Type': "application/json",
                    'cache-control': "no-cache"
                }
                response = requests.request(
                    "GET", 
                    url, 
                    data=payload, 
                    headers=headers, 
                    params=querystring
                )
                if response.text:
                    jsonResponse = json.loads(response.text)
                
                result['hierarchies'].extend(jsonResponse['hierarchies'])
        
        except requests.exceptions.ConnectTimeout:
            logging.error("TSIClient: The request to the TSI api timed out.")
            raise
        except requests.exceptions.HTTPError:
            logging.error("TSIClient: The request to the TSI api returned an unsuccessfull status code.")
            raise

        return result

    def writeHierarchies(self, payload):
        jsonResponse = self._updateTimeSeries(payload, 'hierarchies')
        return jsonResponse
    
    def _updateTimeSeries(self, payload, timeseries):
        """Writes instances to the TSI environment.

        Args:
            payload (str): A json-serializable payload that is posted to the TSI environment.
                The format of the payload is specified in the Azure TSI documentation.

        Returns:
            dict: The response of the TSI api call.
        """

        authorizationToken = self.authorization_api._getToken()

        url = "https://{environmentId}.env.timeseries.azure.com/timeseries/{timeseries}/$batch".format(environmentId=self.environmentId,timeseries=timeseries)
        
        querystring = self.common_funcs._getQueryString()

        headers = {
            'x-ms-client-application-name': self._applicationName,
            'Authorization': authorizationToken,
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring)

        if response.text:
            jsonResponse = json.loads(response.text)

        return jsonResponse