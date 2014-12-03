from bs4 import BeautifulSoup as BS
import requests
import csv
import re

URLS_FILE = "urls.txt"

headers = [ "Sponsor(s)", 
            "First Name", 
            "Last Name", 
            "Tag", 
            "Twitter", 
            "2014 Rank", 
            "2013 Rank", 
            "Main(s)", 
            "Region", 
            "Rating",
            "Apex 2014",
            "MLG 2014",
            "CEO 2014",
            "EVO 2014",
            "TBH4" ]
def get_ranking_csv(outfilename):
    global headers
    urls = []
    with open(URLS_FILE, "r") as fin:
        for l in fin:
            urls.append(l.strip())

    output = get_rankings(urls)
    
    with open(outfilename, "w") as fout:
        writer = csv.writer(fout, delimiter=',')
        writer.writerow(headers)
        for row in output:
            writer.writerow(row)

def get_rankings(urls):
    output = []
    for url in urls:
        output.extend(get_rankings_for_url(url))
    return output

def get_rankings_for_url(url):
    print 'get_rankings(url): ' + str(url)
    r = requests.get(url)
    return parse_rankings_page(r.text)

tourneys = ["apex", "mlg", "ceo", "evo", "tbh"]
quotes = re.compile(u'[\u201c\u201d\u2033\"]')
def parse_rankings_page(html):
    global tourneys
    global quotes
    soup = BS(html)
    
    content = soup.find("div", class_="post-content")
    tbodies = content.select("table > tbody")


    ret = []
    for tbody in tbodies:
        rows = tbody.select("tr")
        player_info = list(rows[0].select("td")[1].strong.strings)

        twitter = player_info[-1] if len(player_info) > 1 else ""

        sponsor_name_and_tag = player_info[0].rstrip(" |")
        
        split_sponsor_name_and_tag = [i.strip() for i in sponsor_name_and_tag.split("|")]
        name_and_tag = split_sponsor_name_and_tag[-1]

        if len(split_sponsor_name_and_tag) > 1:
            sponsors = ', '.join(split_sponsor_name_and_tag[:-1])
        else:
            sponsors = ''

        first, tag, last = [i.strip() for i in re.split(quotes, name_and_tag)]

        rank = rows[1].select("td")[0].text.strip()
        previous_rank = rows[1].select("td")[1].text.strip()
        mains = rows[1].select("td")[3].text.strip()
        region = rows[1].select("td")[5].text.strip()

        rating = rows[1].select("td")[6].text.strip()

        results = {}
        for i in xrange(len(tourneys)):
            results[tourneys[i]] = rows[4].select("td")[i].text.strip()

        player_parsed = [sponsors, first, last, tag,
            twitter, rank, previous_rank, mains, region, rating]
        player_parsed.extend([results[t] for t in tourneys])
        player_parsed = [i.replace(u'\xa0', ' ') for i in player_parsed]
        print player_parsed
        ret.append(player_parsed)

    return ret

def main():
    get_ranking_csv("rankings.csv")

if __name__ == "__main__":
    main()

