from bs4 import BeautifulSoup as BS
import requests
import unicodecsv
import re
import numpy as np
import matplotlib.pyplot as plt
import itertools
import string

URLS_FILE = "urls.txt"

headers = [ "Sponsor(s)", 
            "First Name", 
            "Last Name", 
            "Tag", 
            "Twitter", 
            "2014 Rank", 
            "2013 Rank", 
            "Change in Rank",
            "Main(s)", 
            "Region", 
            "Rating",
            "Apex 2014",
            "MLG 2014",
            "CEO 2014",
            "EVO 2014",
            "TBH4" ]
def save_ranking_csv(outfilename):
    global headers
    urls = []
    with open(URLS_FILE, "r") as fin:
        for l in fin:
            urls.append(l.strip())

    data = get_rankings(urls)
    
    with open(outfilename, "w") as fout:
        writer = unicodecsv.UnicodeWriter(fout, delimiter=',')
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

    return data

def get_rankings(urls):
    return list(itertools.chain(*[get_rankings_for_url(url) for url in urls]))

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
        rows = tbody.select("> tr")
        if rows[0].select("td")[0].text != 'Rank':
            continue
        player_info = [i for i in rows[0].select("td")[1].strings if len(i) > 1]

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

        previous_rank_numstr = previous_rank.strip('() ')
        rank_delta_str = 'N/A'
        if previous_rank_numstr.isdigit():
            rank_delta = int(previous_rank_numstr) - int(rank)
            if rank_delta >= 0:
                rank_delta_str = "+" + str(rank_delta)
            else:
                rank_delta_str = str(rank_delta)

        mains = rows[1].select("td")[3].text.strip()
        results = {}

        if mains == '': # Tafo why did you format #1 and 2 differently
            print tag, "mains: ", mains, "."
            mains = string.capwords(', '.join([img['alt'] for img in rows[1].select("td")[3].select("img")]).strip('9 '), ', ')
            region = rows[2].select("td")[1].text.strip()
            rating = rows[1].select("> td")[4].text.strip()
            for i in xrange(len(tourneys)):
                results[tourneys[i]] = rows[5].select("td")[i].text.strip()
        else:
            region = rows[1].select("td")[5].text.strip()
            rating = rows[1].select("td")[6].text.strip()
            for i in xrange(len(tourneys)):
                results[tourneys[i]] = rows[4].select("td")[i].text.strip()


        player_parsed = [sponsors, first, last, tag,
            twitter, rank, previous_rank, rank_delta_str, mains, region, rating]
        player_parsed.extend([results[t] for t in tourneys])
        player_parsed = [i.replace(u'\xa0', ' ') for i in player_parsed]

        print player_parsed
        ret.append(player_parsed)

    return ret

def scatter_plot_ranking_vs_rating(data, fname):
    global headers
    ranking_idx = headers.index("2014 Rank")
    rating_idx = headers.index("Rating")

    rankings = np.array([int(row[ranking_idx]) for row in data])
    ratings = np.array([float(row[rating_idx]) for row in data])

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_xlabel("Rank")
    ax.set_ylabel("Rating")
    ax.grid(b=True, which='major', color='gray', linestyle='--')
    ax.scatter(rankings, ratings)
    plt.show()

    fig.savefig(fname, orientation="landscape", dpi=100)

def main():
    data = save_ranking_csv("rankings.csv")
    scatter_plot_ranking_vs_rating(data, "ranking_vs_rating.png")

if __name__ == "__main__":
    main()

