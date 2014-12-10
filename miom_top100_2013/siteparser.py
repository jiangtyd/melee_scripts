from bs4 import BeautifulSoup as BS
import requests
import unicodecsv
import re
import numpy as np
import matplotlib.pyplot as plt
import itertools

URLS_FILE = "urls.txt"

headers = [ "First Name", 
            "Last Name", 
            "Tag", 
            "2013 Rank", 
            "Main(s)", 
            "Region", 
            "Rating" ]

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

quotes = re.compile(u'[\u201c\u201d\u2033\"]')
def parse_rankings_page(html):
    global quotes
    soup = BS(html)
    
    content = soup.find("div", class_="post_content")
    tables = content.select("table")

    ret = []
    for table in tables:
        tbody = table.select("tbody")[0]
        rows = tbody.select("tr")

        if rows[0].select("td")[0].string.strip() != "Rank":
            break

        player_info = [i for i in rows[0].select("td")[1].strings if len(i) > 1]

        name_and_tag = player_info[0].rstrip(u"\xa0 |")
        
        first, tag, last = [i.strip() for i in re.split(quotes, name_and_tag)]

        rank = rows[1].select("td")[0].text.strip("(Ttie) ")
        region = rows[1].select("td")[2].text.strip()
        rating = rows[1].select("td")[3].text.strip()
        # MIOM pls why can't you give Mango a real numerical rating
        if rating == "1o":
            rating = "10"

        mains = rows[2].select("td")[1].text.strip()

        results = {}

        player_parsed = [first, last, tag,
            rank, mains, region, rating]
        player_parsed = [i.replace(u'\xa0', ' ') for i in player_parsed]

        print player_parsed
        ret.append(player_parsed)

    return ret

def scatter_plot_ranking_vs_rating(data, fname):
    global headers
    ranking_idx = headers.index("2013 Rank")
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
    data = save_ranking_csv("rankings_2013.csv")
    scatter_plot_ranking_vs_rating(data, "ranking_vs_rating_2013.png")

if __name__ == "__main__":
    main()

