import sys
from make_client.make_client import make_client

from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v8 import GoogleAdsServiceClient
from dotenv import dotenv_values

import csv
import os


def get_search_terms_and_save_to_csv(account_id, mcc_id="", filename="search_terms.csv"):
    """
    :param account_id: ID of the account you want to access
    :param mcc_id: ID of the MCC if the user who has access to the token only can access via an MCC
    (not directly added to the account)
    :param filename: Name of the file you want saved
    :return: null
    """
    # make the filename where the results are stored
    full_file_name = os.path.join("../query_cache", filename)

    # Make the client
    client = make_client(mcc_id)
    ga_service: GoogleAdsServiceClient = client.get_service("GoogleAdsService")

    # Make your query
    # https://developers.google.com/google-ads/api/fields/v10/search_term_view_query_builder
    query = """
    SELECT 
        search_term_view.search_term, 
        campaign.name, metrics.cost_micros, 
        metrics.conversions, 
        metrics.ctr, 
        metrics.clicks, 
        metrics.average_cpc, 
        metrics.top_impression_percentage, 
        metrics.absolute_top_impression_percentage, 
        metrics.impressions, 
        metrics.cost_per_conversion 
    FROM 
        search_term_view 
    WHERE 
        metrics.clicks > 2
    ORDER BY 
        metrics.clicks DESC
        """

    # Issues a search request using streaming.
    search_request = client.get_type("SearchGoogleAdsStreamRequest")

    # Set the account ID
    search_request.customer_id = account_id

    # Set the query to the search_request
    search_request.query = query

    # Create the stream
    stream = ga_service.search_stream(search_request)

    # Open the file
    with open(full_file_name, mode='w', encoding="utf-8") as results:

        # Create the CSV Writer and add the header columns
        results_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(
            ['search_term', 'name', 'cost', 'conversions', 'ctr', 'clicks', 'cpc', 'top_is', 'abs_top_is',
             'impressions',
             'date', 'cpa'])

        # Iterate through the stream
        for batch in stream:
            for row in batch.results:
                # Destructure the variables
                metrics = row.metrics
                segments = row.segments
                campaign = row.campaign
                search_term_view = row.search_term_view

                # Write each row
                results_writer.writerow(
                    [search_term_view.search_term, campaign.name, metrics.cost_micros, metrics.conversions, metrics.ctr,
                     metrics.clicks, metrics.average_cpc,
                     metrics.top_impression_percentage, metrics.absolute_top_impression_percentage, metrics.impressions,
                     segments.date, metrics.cost_per_conversion])


if __name__ == "__main__":
    config = dotenv_values("../.env")
    try:
        get_search_terms_and_save_to_csv(config["account_id"], config["mcc_id"])
    except GoogleAdsException as ex:
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
