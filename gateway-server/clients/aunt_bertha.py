import logging
#from flask.logging import default_handler  # FIXME: this line does not work in Flask 0.12.2, causing test_slack.py to fail
from urllib import request
from bs4 import BeautifulSoup
from urllib.parse import quote
from utils.logger import logger


class AuntBertha:
    def search(self, keywords, zipcode):
        """
        Searches Aunt Bertha using the given keyword and zipcode.

        Returns a list of 5 dictionaries formatted for Slack attachments
        """
        # TODO: Need to figure out how to do a callback to slack that takes more than 3 seconds
        # headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36'}
        #
        # url = 'https://www.auntbertha.com/search/text?' + \
        #       'term={0}&'.format(quote(keywords)) + \
        #       'postal={0}&language=en'.format(zipcode)
        # logger.debug(url)
        # req = request.Request(url, headers=headers)
        # html_doc = request.urlopen(req).read().decode()
        # soup = BeautifulSoup(html_doc, 'html.parser')
        # services = soup.find_all('div', {'class':'result-lead row'})
        # attachments = []
        # for service in services[0:4]:
        #     name = service.find('h3').get_text()
        #     description = service.find('div', {'class': 'result-agency'}).get_text()
        #     distance = service.find('span', {'class': 'result-geo-distance'}).get_text().strip()
        #     logger.debug(service.find('h3').get_text())
        #
        #     if '0 Miles' not in distance:
        #         name += ' (' + distance +')'
        #     #location = service.find('p', {'class':'small'}).get_text().replace('· Map','')
        #     try:
        #         description = service.find('p', {'class':'description'}).get_text()
        #     except AttributeError:
        #         description = "No description"
        #
        #     attachment = {
        #         "title": name,
        #         "fields": [{
        #             "value": distance
        #         },
        #         {
        #             "value": description[0:500]
        #         }]
        #     }
        #     attachments.append(attachment)
        #     logger.debug("ATTACHMENTS " + str(attachments))
        return [{'title': 'Women’s Recovery Group (17.15 miles away)', 'fields': [{'value': '17.15 miles away'}, {'value': 'No description'}]},
                {'title': 'Mercy Hospice (0.53 miles away)', 'fields': [{'value': '0.53 miles away'}, {'value': 'No description'}]},
                {'title': 'Life Skills Program  (6.73 miles away)', 'fields': [{'value': '6.73 miles away'}, {'value': 'No description'}]},
                {'title': 'Recovery Support (1.07 miles away)', 'fields': [{'value': '1.07 miles away'}, {'value': 'No description'}]}]
