from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re
import time


def get_links(initial_link):
    list_of_cursor_links = [initial_link]

    def get_links_lower_level(link):

        response = urlopen(link)
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        regex_cursor = re.compile(r'(?<=href=").\D+.\d+')
        cursor_tag = str(soup.find('div', class_="w-button-more"))
        cursor_link = regex_cursor.findall(cursor_tag)[0]
        cursor_link = f'https://mobile.twitter.com' + cursor_link
        list_of_cursor_links.append(cursor_link)
        print(cursor_link)

        try:
            get_links_lower_level(cursor_link)

        except Exception as e:
            print(e)
            print('END OF CURSOR LINKS')

    get_links_lower_level(initial_link)

    return list_of_cursor_links


def get_followers_dictionaries(list_of_cursor_links):
    followers_list = []

    regex_name = re.compile(r'(?<=name=").\w+')
    regex_img = re.compile(r'(?<=src=).*\w.')

    for c_link in list_of_cursor_links:

        try:
            response = urlopen(c_link)
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            followers_info = soup.findAll('table', class_="user-item")

            for follower_info in followers_info:
                fullname = follower_info.find('strong', class_="fullname").getText()

                username = str(follower_info.find('td', class_="info"))
                username = regex_name.findall(username)[0]

                img = str(follower_info.find('img', class_="profile-image"))
                img = regex_img.findall(img)[0]

                user_link = f'https://mobile.twitter.com/{username}'

                user_info = {'fullname': fullname, 'username': username, 'img': img, 'user_link': user_link}
                followers_list.append(user_info)

        except Exception as e:
            print(e)
            pass

    return followers_list


def data_frame_builder(followers_list):
    df = pd.DataFrame(followers_list)
    return df


def get_following_simple(user):
    initial_link = 'https://mobile.twitter.com/' + user + '/following'

    list_of_cursor_links = get_links(initial_link)
    followers_list = get_followers_dictionaries(list_of_cursor_links)
    data_frame = data_frame_builder(followers_list)

    return data_frame


def get_followers_simple(user):
    initial_link = 'https://mobile.twitter.com/' + user + '/followers'

    list_of_cursor_links = get_links(initial_link)
    followers_list = get_followers_dictionaries(list_of_cursor_links)
    data_frame = data_frame_builder(followers_list)

    return data_frame


def get_following_complete(user):
    df = get_following_simple(user)

    list_of_user_complete_info = []

    counter = 1

    for link in df['user_link']:

        try:
            time.sleep(1)
            response = urlopen(link)
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            location = soup.find('div', class_='location').getText()
            bio = soup.find('div', class_='bio').getText().strip()
            url = soup.find('div', class_='url').getText().strip()
            stats = soup.findAll('div', class_='statnum')
            number_of_tweets = int(stats[0].getText().replace(",", ""))
            number_of_following = int(stats[1].getText().replace(",", ""))
            number_of_followers = int(stats[2].getText().replace(",", ""))

            list_of_user_complete_info.append({'location': location,
                                               'bio': bio,
                                               'url': url,
                                               'number_of_tweets': number_of_tweets,
                                               'number_of_following': number_of_following,
                                               'number_of_followers': number_of_followers
                                               })

            print(f'{counter}/{len(df)}', location, bio, url, number_of_tweets, number_of_following,
                  number_of_followers)
            counter += 1

        except Exception as e:
            print(f'{counter}/{len(df)}', e)
            pass
            counter += 1

    df1 = pd.DataFrame(list_of_user_complete_info)
    df = pd.concat([df, df1], axis=1)
    return df


def get_followers_complete(user):
    df = get_followers_simple(user)

    list_of_user_complete_info = []

    counter = 1

    for link in df['user_link']:

        try:

            time.sleep(1)
            response = urlopen(link)
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            location = soup.find('div', class_='location').getText()
            bio = soup.find('div', class_='bio').getText().strip()
            url = soup.find('div', class_='url').getText().strip()
            stats = soup.findAll('div', class_='statnum')
            number_of_tweets = int(stats[0].getText().replace(",", ""))
            number_of_following = int(stats[1].getText().replace(",", ""))
            number_of_followers = int(stats[2].getText().replace(",", ""))

            list_of_user_complete_info.append({'location': location,
                                               'bio': bio,
                                               'url': url,
                                               'number_of_tweets': number_of_tweets,
                                               'number_of_following': number_of_following,
                                               'number_of_followers': number_of_followers
                                               })

            print(f'{counter}/{len(df)}', location, bio, url, number_of_tweets, number_of_following,
                  number_of_followers)
            counter += 1

        except Exception as e:
            print(f'{counter}/{len(df)}', e)
            counter += 1
            pass

    df1 = pd.DataFrame(list_of_user_complete_info)
    df = pd.concat([df, df1], axis=1)
    return df


def main_function():
    user = input("What is the USERNAME?: \n").strip().strip('@')
    action = input("Do you want to scrape FOLLOWERS or FOLLOWING?: \n").lower().strip()
    mode = input("Do you want to scrape in SIMPLE or COMPLETE mode?: \n").lower().strip()
    print('\n')

    try:

        if (mode == 'simple') & (action == 'followers'):
            df = get_followers_simple(user)
            df.to_csv(f'{user}_followers_simple.csv', index=False)

        if (mode == 'simple') & (action == 'following'):
            df = get_following_simple(user)
            df.to_csv(f'{user}_following_simple.csv', index=False)

        if (mode == 'complete') & (action == 'followers'):
            df = get_followers_complete(user)
            df.to_csv(f'{user}_followers_complete.csv', index=False)

        if (mode == 'complete') & (action == 'following'):
            df = get_following_complete(user)
            df.to_csv(f'{user}_following_complete.csv', index=False)

    except Exception as e:
        print('\n', e)
        print('\n Something went wrong, please try again... \n')
        time.sleep(1)
        main_function()


main_function()
