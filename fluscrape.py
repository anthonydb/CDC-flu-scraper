import re
import csv
import requests
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

    # open url
    if verbose:
        print "Opening url ..."
    url = "http://www.cdc.gov/flu/weekly/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text)

    # open and prep outfile
    outfile = open('flu.csv', 'wb')
    outwriter = csv.writer(outfile, delimiter=",")
    headers = [
        'WEEK_NUM', 'WEEK_END', 'HHS_REGION', 'OUTPATIENT_ILI', 'PCT_FLU_POS',
        'NUM_JURIS', '2009_H1N1', 'A_H3', 'A_NO_SUBTYPE', 'B', 'PED_DEATHS'
    ]
    outwriter.writerow(headers)

    # use regex to get the week number and ending date
    week_text = re.search(r'Week (\d{1,2}) ending (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})', r.text)
    week_num = week_text.group(1)
    week_end = week_text.group(2) + ' ' + str(week_text.group(3)) + ', ' + str(week_text.group(4))
    if verbose:
        print 'Found week number ' + week_num
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
        pct = col[3].string.strip('%')
        num_juris = col[2].string
        a_2009_h1n1 = col[4].string
        a_h3 = col[5].string
        a_no_subtype = col[6].string
        b = col[7].string
        ped_deaths = col[8].string
        parsed_row = (
            week_num, week_end, region, ili, pct, num_juris, a_2009_h1n1, a_h3,
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
