from site_API.core import SiteApi
from config import AppSettings

app = AppSettings()
site = SiteApi(app.site_api.get_secret_value(), app.host_api)

response_json = site.get_high(3)
for i in response_json["results"]:
    print(i)
