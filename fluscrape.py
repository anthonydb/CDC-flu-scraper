import re
import csv
import mechanize
import cookielib
import simplejson
from bs4 import BeautifulSoup


def run(verbose=True):
    """
    Scrapes the weekly "National and Regional Summary of Select
    Surveillance Components" table from the Centers for Disease
    Control's flu summary site at http://www.cdc.gov/flu/weekly/

    Exports data to comma-delimited text and json file.

    Example usage:

        >>> import fluscrape
        >>> fluscrape.run()

        $ python fluscrape.py
    """

    if verbose:
        print 'Initializing ...'

    # prep browser
    br = mechanize.Browser()
    # tell it to ignore robots.txt
    br.set_handle_robots(False)
    # add cookie capabilities if needed
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    # Use Chrome browser headers
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1')]

    # open url
    if verbose:
        print "Opening url ..."
    url = "http://www.cdc.gov/flu/weekly/"
    br.open(url)
    html = br.response().read()
    soup = BeautifulSoup(html)

    # open and prep outfile
    outfile = open('flu.csv', 'wb')
    outwriter = csv.writer(outfile, delimiter=",")
    headers = [
        'WEEK_NUM', 'WEEK_END', 'HHS_REGION', 'OUTPATIENT_ILI', 'PCT_FLU_POS',
        'NUM_JURIS', 'A_H3', 'A_2009_H1N1', 'A_NO_SUBTYPE', 'B', 'PED_DEATHS'
    ]
    outwriter.writerow(headers)

    # use regex to find the week number
    week_num_text = re.search(r'Influenza Season Week \d{1,2}', html)
    week_num = week_num_text.group()
    week_num = re.sub('Influenza Season Week ', '', week_num)
    if verbose:
        print 'Found week number ' + week_num

    # use regex to find the week ending date
    week_end_text = re.search(r'ending (January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}', html)
    week_end = week_end_text.group()
    week_end = re.sub('ending ', '', week_end)
    if verbose:
        print 'Found week ending ' + week_end

    # locate and parse table
    if verbose:
        print 'Parsing table ...'

    table = soup.find("table", cellpadding=3)

    # go get the data
    row_counter = 1
    for row in table.findAll('tr')[2:]:
        name = row.findAll('strong')
        region = name[0].string
        col = row.findAll('td')
        ili = col[1].string
        pct = col[2].string.strip('%')
        num_juris = col[3].string
        a_h3 = col[4].string
        a_2009_h1n1 = col[5].string
        a_no_subtype = col[6].string
        b = col[7].string
        ped_deaths = col[8].string
        parsed_row = (
            week_num, week_end, region, ili, pct, num_juris, a_h3, a_2009_h1n1,
            a_no_subtype, b, ped_deaths
        )
        if verbose:
            print 'Printing row ' + str(row_counter)
        outwriter.writerow(parsed_row)
        row_counter += 1

    outfile.close()

    # reopen CSV data
    infile = open('flu.csv', 'r')
    data = csv.DictReader(infile)
    # convert to JSON
    json = simplejson.dumps(list(data), indent=4)
    # write to file
    jsonfile = open("flu.json", "w")
    jsonfile.write(json)
    jsonfile.close()
    infile.close()

    # wrap up
    if verbose:
        print 'All done!'


if __name__ == '__main__':
    run()
