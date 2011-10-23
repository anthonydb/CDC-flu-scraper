import csv
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup


def run(verbose=True):
    """
    Scrapes the weekly "National and Regional Summary of Select 
    Surveillance Components" table from the Centers for Disease
    Control's flu summary site at http://www.cdc.gov/flu/weekly/

    Exports the data to a pipe-delimited text file.
    
    Example usage:

        >>> import scrape
        >>> scrape.run()
        
        $ python scrape.py

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
    outfile = csv.writer(open('flu.csv', 'w'), delimiter="|")
    headers = [
        'WEEK', 'HHS_REGION', 'OUTPATIENT_ILI', 'PCT_FLU_POS',
        'NUM_JURIS', 'A_H3', 'A_2009_H1N1', 'A_NO_SUBTYPE', 'B', 'PED_DEATHS'
    ]
    outfile.writerow(headers)

    # locate and parse table
    if verbose:
        print 'Parsing table ...'

    table = soup.find("table", cellpadding=3)

    # figure out the week
    for row in table.findAll('tr')[0:1]:
        x = row.findAll('th')
        week = x[1].string.strip('Data for week ')

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
            week, region, ili, pct, num_juris, a_h3, a_2009_h1n1, 
            a_no_subtype, b, ped_deaths
        )
        if verbose:
            print 'Printing row ' + str(row_counter)
        outfile.writerow(parsed_row)
        row_counter += 1

    # wrap up
    if verbose:
        print 'All done!'


if __name__ == '__main__':
    run()
