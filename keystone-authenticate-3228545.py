__author__          = 'agsvn'

    # Foundation:   3228545
    # UX:           3228545
    # Version:      20.5.0
    # Branch:       10.11.322.2991 (league-of-legends)
    
    def keystoneSession(self):
        self.did = self.randomString(32, True)
        self.nonce = f"{self.randomString(8, False)}_{self.randomString(13, False)}"
        headers = {
            'Accept-Encoding': 'deflate, gzip', 
            'user-agent': self.userAgent('rso'), 
            'Cache-Control': 'no-cache', 
            'Content-Type': 'application/json', 
            'Cookie': f'did={self.did}', 
            'Accept': 'application/json'
        }

        payload = {
            'acr_values': 'urn:riot:bronze',
            'claims': '',
            'client_id': 'riot-client',
            'nonce': self.nonce,
            'redirect_uri': 'http://localhost/redirect',
            'response_type': 'token id_token',
            'scope': 'openid link ban lol_region'
        }

        r = requests.post("https://auth.riotgames.com/api/v1/authorization", headers=headers, json=payload)
        if r.status_code == 200:
            cookies = r.headers['Set-Cookie']
            self.asid = f"{re.search('asid=(.*)%3D;', cookies).group(1)}%3D"
            self.clid = re.search('clid=(.*); Path', cookies).group(1)
        else:
            raise Exception("something went wrong, failed to create session")

    def keystoneAuthorize(self, username: str=None, password: str=None, region: str=None):
        self.platform = self.system["region_data"][region]["rso_platform_id"]
        self.serviceLocation = self.system["region_data"][region]["servers"]["discoverous_service_location"]


        headers = {
            'Accept-Encoding': 'deflate, gzip', 
            'user-agent': self.userAgent('rso'), 
            'Cache-Control': 'no-cache', 
            'Content-Type': 'application/json', 
            'Cookie': f'did={self.did}; asid={self.asid}; clid={self.clid}', 
            'Accept': 'application/json'
        }

        payload = {
            'language': 'en_GB',
            'password': password,
            'region': region,
            'remember': False,
            'type': 'auth',
            'username': username
        }

        r = requests.put("https://auth.riotgames.com/api/v1/authorization", headers=headers, json=payload)
        
        data = r.text
        cookies = r.headers['Set-Cookie']
        self.accessToken = re.search('access_token=(.*)&token_type=Bearer', data).group(1)
        self.idToken = re.search('id_token=(.*)&token_type=Bearer', data).group(1)

        self.sub = re.search('sub=(.*); Path', cookies).group(1)
        self.ssid = re.search('ssid=(.*); Path', cookies).group(1)
        self.ssalt = re.search('ssalt=(.*); Path', cookies).group(1)
        

        _accessTokenPayload = json.loads(base64.b64decode(self.fixTokenPayload(self.accessToken.split('.')[1])))
        _idTokenPayload = json.loads(base64.b64decode(self.fixTokenPayload(self.idToken.split('.')[1])))

        self.puuid = _accessTokenPayload["sub"]
        self.accountId = _accessTokenPayload["dat"]["u"]
