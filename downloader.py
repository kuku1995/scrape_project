import requests
import logging
logging.basicConfig(filename='imdb_log_file.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


class DownloadException(Exception):
    """
    Created for raising error if page was not found when requesting access
    """
    pass


class Downloader:
    """
    Creating objects of download requests from IMDb
    """

    @staticmethod
    def download(url):
        """
        Requesting access to the IMDb site and extracting textual content
        """
        try:
            # Requesting access to site
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.error(f'Invalid website access request: {url}')
            raise DownloadException("Could not find page")
        else:
            print(url, 'Access to site is approved')
            logging.info(f'Website successfully accessed: {url}')

            return response.text


