from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import dotenv_values


# Make refresh token here:
# https://developers.google.com/oauthplayground/#step1&scopes=https%3A//www.googleapis.com/auth/adwords&url=https%3A//&content_type=application/json&http_method=GET&useDefaultOauthCred=checked&oauthEndpointSelect=Google&oauthAuthEndpointValue=https%3A//accounts.google.com/o/oauth2/v2/auth&oauthTokenEndpointValue=https%3A//oauth2.googleapis.com/token&includeCredentials=unchecked&accessTokenType=bearer&autoRefreshToken=unchecked&accessType=offline&forceAprovalPrompt=checked&response_type=code
def make_client(mcc_id="") -> GoogleAdsClient:
    """
    :param mcc_id: this is the ID of the MCC the user is attached to. If the User has direct access to an account,
    don't pass a value here. If the user only has access to an account via an MCC. Pass through the MCC ID here.
    :return: GoogleAdsClient
    """
    config = dotenv_values("../.env")
    credentials = {
        "developer_token": config["developer_token"],
        "refresh_token": config["refresh_token"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "use_proto_plus": True
    }
    google_ads_client = GoogleAdsClient.load_from_dict(credentials, version="v10")
    if mcc_id != "":
        google_ads_client.login_customer_id = mcc_id
    return google_ads_client


if __name__ == "__main__":
    try:
        make_client()
    except GoogleAdsException as ex:
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
