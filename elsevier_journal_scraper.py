# -*- coding: utf-8 -*-
"""
This script scrapes the Elsevier website to get a list of journals that are part
of the TLCUA read & publish agreement.

It assumes the webpage with the title list is https://agreements.journals.elsevier.com/tlcua?pageNo=1
The script will iterate through each page of results on that website. The script
will ask for the maximum number of pages to scrape (can be found at the bottom
of the title list webpage).

Results are saved as an ANSI-encoded CSV file (ANSI encoded to be easy to open
with Excel).

Created by Elliot Williams on Feb 25 2026.
"""

import csv
import requests
from bs4 import BeautifulSoup

def scrape_data(scrape_url):
    """Scrape URL and parse with BeautifulSoup"""
    page = requests.get(scrape_url, timeout=5)
    page.raise_for_status()

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="maincontent")
    return results


def get_journal_metadata(journal):
    """Extract journal metadata from scraped HTML"""

    title = journal.find("h3", class_="search-result-title").text.strip()

    # Reset journal metadata fields, so they will be blank if not found for this journal
    issn = ""
    subject = ""
    oa_type = ""

    # Retrieve and parse elements that include journal metadata fields
    journal_attributes = journal.find_all("div",
        class_="hide-for-large-up small-12 columns columns-tight")

    for attribute in journal_attributes:
        if "ISSN:" in attribute.span.span.text:
            issn = attribute.span.strong.text.strip()
        if "Primary Subject:" in attribute.span.span.text:
            subject = attribute.span.strong.text.strip()
        if "OA Type:" in attribute.span.span.text:
            oa_type = attribute.span.strong.text.strip()

    # Add all metadata fields to a list
    journal_data = [title, issn, subject, oa_type]
    print(journal_data)
    return journal_data


def create_output(all_data):
    """Print journal metadata to CSV"""

    # Create filename to save data as CSV
    output_file = 'elsevier_OA_journals.csv'

    # Define header row for output file
    header = ['Title','ISSN','Subject','OA Type']

    # Write CSV
    with open(output_file, 'w', encoding='ansi', newline='') as outfile:
        write = csv.writer(outfile)
        write.writerow(header)
        write.writerows(all_data)

    outfile.close()


def main():

    # Set URL to query
    base_url = "https://agreements.journals.elsevier.com/tlcua?pageNo="

    # Set maximum number of pages to scrape
    # Change this number to the max number of pages on the Elsevier website to be scraped
    while True:
        try:
            max_pages = int(input("How many pages of results need to be scraped? "))
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Change this number if you want to start at a page other than 1
    n = 1

    # Create empty list to hold journal metadata
    all_data = []

    # Iterate through all of the pages to be scraped, and stop when max page limit is reached
    while n <= max_pages:

        scrape_url = base_url + str(n)

        print(scrape_url)

        # Get data by scraping this page
        results = scrape_data(scrape_url)

        # Get journal elements from HTML
        journals = results.find_all("div", class_="row row-tight-all open-access-journal-result")

        # Iterate through each journal and extract metadata
        for journal in journals:
            journal_data = get_journal_metadata(journal)

            # Append this journal's metadata to the overall list
            all_data.append(journal_data)

        # Increment page number for next scrape
        n += 1

    # Save data to CSV
    create_output(all_data)


if __name__ == '__main__':
    main()
