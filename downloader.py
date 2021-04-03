import requests


class DownloadException(Exception):
    """
    Created for raising error if page was not found when requesting access
    """
    pass


class Downloader:
    """
    Creating objects of access requests from IMDb
    """

    @staticmethod
    def download(url, logger):
        """
        Requesting access to the IMDb site and extracting textual content
        """
        try:
            # Requesting access to site
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logger.critical(f'Invalid URL, unable to scrape site: {url}')
            raise DownloadException(f'Invalid URL, unable to scrape site: {url}')
        else:
            logger.info(f'{url} successfully accessed')

            return response.text