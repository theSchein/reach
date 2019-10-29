from urllib import request
from bs4 import BeautifulSoup

class TwoOneOne:
    def search(self, keyword, zipcode):
        """
        Searches 211 using the given keyword and zipcode.

        Returns a list of 5 dictionaries formatted for Slack attachments
        """
        url = 'http://pa211.communityos.org/zf/profile/search?' + \
              'keyword={0}&'.format(keyword) + \
              'distance_zip={0}&'.format(zipcode) + \
              'dosearch=1&Search=Search#'
        html_doc = request.urlopen(url).read().decode()
        soup = BeautifulSoup(html_doc, 'html.parser')
        services = soup.find_all('div', {'class':'search_result'})
        attachments = []
        for service in services[0:5]:
            name = service.find('p', {'class':'service'})
            title = name.find('a').get_text()
            distance = name.find('span', {'class': 'small'}).get_text().strip()
            if '0 Miles' not in distance:
                title += ' (' + distance +')'
            location = service.find('p', {'class':'small'}).get_text().replace('· Map','')
            try:
                description = service.find('p', {'class':'description'}).get_text()
            except AttributeError:
                description = "No description"

            attachment = {
                "title": title,
                "fields": [{
                    "value": location
                },
                {
                    "value": description[0:500]
                }]
            }
            attachments.append(attachment)

        return attachments
