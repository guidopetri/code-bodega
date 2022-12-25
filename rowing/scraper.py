#! /usr/bin/python3

import pandas as pd
import bs4
import requests
import time
from queue import Queue


MAX_URLS = -1
URLS_SET = set()


def build_urls(events, weights, genders):
    global URLS_SET

    urls_queue = Queue()
    base_url = 'https://log.concept2.com/rankings/2023/rower/'

    for event in events:
        for weight in weights:
            for gender in genders:
                url = (base_url
                       + event
                       + '?rower=rower'
                       + f'&weight={weight}'
                       + f'&gender={gender}'
                       + '&page=1'
                       )
                urls_queue.put(url)
                URLS_SET.add(url)

    return urls_queue


def update_queue(queue, url, max_pagenum):
    global URLS_SET

    # remove pagenum from the end
    cleaned_url = url.rstrip('0123456789')

    if cleaned_url + str(max_pagenum) in URLS_SET:
        return

    for page in range(2, max_pagenum + 1):
        new_url = cleaned_url + str(page)
        queue.put(new_url)
        URLS_SET.add(new_url)

    return


def get_data(url, queue):
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
    except Exception as e:
        print(f'Error for url: {url}')
        if r in locals():
            print(r.status_code, r.text)
        print(e)
        return pd.DataFrame()

    soup = bs4.BeautifulSoup(r.text, 'html5lib')

    results = []

    # 1st table in page is the percentiles table
    for row in soup.find_all(class_='table')[1].find('tbody').find_all('tr'):
        result = [td.contents[0]
                  if td.contents
                  else None
                  for td in row.find_all('td')
                  ]
        # unwrap name / url
        result.append(result[1].get('href')[41:])
        result[1] = result[1].contents[0]

        results.append(result)

    df = pd.DataFrame.from_records(results,
                                   columns=['standing',
                                            'name',
                                            'age',
                                            'location',
                                            'country',
                                            'org',
                                            'time',
                                            'verified',
                                            'profile_link',
                                            ]
                                   )

    event_start_idx = url.find('rower/') + 6
    event_end_idx = url.find('?rower=rower')
    event = url[event_start_idx: event_end_idx]

    weight_class_idx = url.find('weight=') + 7
    weight_class = url[weight_class_idx: weight_class_idx + 1]

    gender_idx = url.find('gender=') + 7
    gender = url[gender_idx: gender_idx + 1]

    df['event'] = event
    df['weight_class'] = weight_class
    df['gender'] = gender

    max_pagenum = int(soup.find(class_='pagination-block')
                          .find_all('li')[-2]  # last item is >> (next page)
                          .find('a')
                          .contents[0]
                      )

    update_queue(queue, url, max_pagenum)

    return df


if __name__ == '__main__':
    events = ['1', '4', '30', '60',  # minutes
              '100', '500', '1000', '2000', '5000', '6000', '10000',
              '21097', '42195', '100000',
              ]
    weights = ['H', 'L']
    genders = ['M', 'F']

    urls = build_urls(events, weights, genders)
    data = pd.DataFrame()
    iter_count = 0

    while not urls.empty() and (MAX_URLS == -1 or iter_count < MAX_URLS):
        try:
            url = urls.get()
            print(f'Scraping: {url}')
            data = pd.concat([data, get_data(url, urls)])
            iter_count += 1
            print(f'Scrape successful, data length: {data.shape[0]}, remaining url count: {urls.qsize()}')
            print('Sleeping for 10s', flush=True)
            time.sleep(10)
        except Exception as e:
            print('Error')
            print(e)
    data.to_csv('rowing_data.csv')
