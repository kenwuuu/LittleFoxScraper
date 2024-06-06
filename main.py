import re
import time

import requests
from bs4 import BeautifulSoup


def get_story_urls(url):
    """
    Fetches the content of the given URL, extracts elements with the class 'readers_img_link',
    and constructs their full URLs using the provided base URL.
    :return list of urls
    """
    output = []

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    readers_img_link = soup.find_all('a', class_='readers_img_link')  # Find elements with class 'readers_img_link'

    base_url = 'https://chinese.littlefox.com'  # Assuming the base URL

    for element in readers_img_link:
        href = element.get('href')
        story_name = element.get('data-ga')
        if href:  # Check if href attribute exists
            full_url = f"{base_url}{href}"  # Construct full URL using f-string
            output.append([full_url, story_name])

    return output


def set_url_page_num(url, page_num):
    return url + "&page=" + str(page_num)


def get_chapter_ids_of_story(story_id, page_num):
    """
    returns a list of chapter id's from a given story
    :param story_id: story URL
    :param page_num: which page of the table of contents to open
    :return: array of chapter_ids
    """
    # parse url
    base_url = "https://chinese.littlefox.com/en/story/contents_list/"
    url = base_url + story_id
    set_url_page_num(url, page_num)

    # Parse the HTML content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all 'span' elements with the 'fc_id' attribute
    fc_id_elements = soup.find_all('span', attrs={'fc_id': True})

    # Extract and store unique fc_id's in a set
    unique_fc_ids = set()
    for element in fc_id_elements:
        fc_id = element.get('fc_id')
        unique_fc_ids.add(fc_id)

    # turn into list, and sort
    chapter_ids = sorted(unique_fc_ids)

    return chapter_ids


def chapter_to_text(chapter_id, session, translation=False):
    """

    :param chapter_id:
    :param session: request session
    :param translation: whether to include the English translation in the output
    :return: array of strings
    """

    def format(text):
        # Replace `<br/>` with a newline character
        text = text.replace("<br/>", "")
        text = text.replace("&nbsp;", " ")

        # custom formatting for
        text = text.replace("\n\n", "")
        text = text.replace(" ", "")

        # some AI regex
        pattern = r"\s(?=\S)|\s(?<= \S)|\u00a0"
        text = re.sub(pattern, "", text, flags=re.MULTILINE)

        return text

    # build url
    output = []
    base_url = "https://chinese.littlefox.com/en/supplement/org/"
    url = base_url + chapter_id

    # get url
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract all 'desc' attributes
    desc_attributes = soup.find_all('div', class_='desc')

    # Extract text from 'desc' attribute
    for i, desc_attribute in enumerate(desc_attributes):
        if not translation and i != 0:
            for text_div in desc_attribute.find_all('div', class_=['t0', 't1', 't2']):
                text = text_div.text.strip()
                text = format(text)
                output.append(text)

    print(output)
    return output


def save_and_append(filename, output):
    # Save the output to a text file
    # append if file exists
    with open(filename, "a", encoding="utf-8") as f:
        f.write("\n".join(output))
        f.write("\n\n")


def save(filename, output):
    # Save the output to a text file
    # append if file exists
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
        f.write("\n\n")


def get_chapter_transcripts(chapter_ids, session):
    """

    :param chapter_ids: array of chapter_ids
    :return: dictionary of {chapter_id: "transcript"}
    """

    output = ""

    # build chapter URL
    for id in chapter_ids:
        url = "https://chinese.littlefox.com/en/supplement/org/" + id
        print(url)

        # access URL and parse transcript content
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        print(response.text)

        # build dictionary with 'title' and 'desc' keys, with values being their text contents
        transcript_data = {}

        for div in soup.find_all('div', class_='txt_box'):
            title_div = div.find('div', class_='title')
            title_text = title_div.find('div', class_='txt0').text.strip()
            desc_div = div.find('div', class_='desc')
            desc_text = ''
            for p in desc_div.find_all('p'):
                desc_text += p.find('span').text.strip() + '\n'
            transcript_data[title_text] = desc_text.strip()

        # print the transcript data
        for title, desc in transcript_data.items():
            output = desc
            print(f"Title: {title}")
            print(f"Description:\n{desc}")
            print("-------------------------")

    return output


def get_table_of_contents_pages(story_id, session):
    """

    :param story_id: story ID
    :param session:
    :return: integer, the number of pages a story's table of contents has
    """
    response = session.get(story_id)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table within the 'lf_paging' div
    paging_table = soup.find('div', class_='lf_paging').find('table')

    # Find all anchor tags (a) containing page numbers
    page_links = paging_table.find_all('a', text=lambda text: text and text.isdigit())

    # Extract the page numbers from the text content
    page_numbers = [int(link.text) for link in page_links]

    # Get the last page number (assuming it's the highest)
    last_page = max(page_numbers)

    return last_page


def reconstruct_story():
    """
    given a story dictionary, combines chapters into a single txt file. saves to a file named after the dict key

    :return:
    """


def get_next_page_url(url):
    """
    This function constructs the URL for the next page in a pagination scheme,
    assuming the page parameter format is "&page=X".

    Args:
        url: The URL of the current page.

    Returns:
        The URL for the next page, or the original URL if no pagination is detected.

    >>> get_next_page_url('https://chinese.littlefox.com/en/story/contents_list/DP000755')
    'https://chinese.littlefox.com/en/story/contents_list/DP000755&page=2'

    >>> get_next_page_url('https://chinese.littlefox.com/en/story/contents_list/DP000756&page=5')
    'https://chinese.littlefox.com/en/story/contents_list/DP000756&page=6'

    >>> get_next_page_url('https://chinese.littlefox.com/en/story/contents_list/DP000755&page=2')
    'https://chinese.littlefox.com/en/story/contents_list/DP000755&page=3'
    """
    if '&page=' in url:
        # Split URL at "&page=" and increment page number (assuming integer)
        return url.split('&page=')[0] + '' + str(int(url.split('=')[-1]) + 1)
    else:
        # No page parameter, add "&page=2"
        return url + '&page=2'


def login(session):
    url = "https://chinese.littlefox.com/en/login/auth_process"

    payload = 'base_pw=&fail_url=&is_changed=0&loginid=matriax1%40gmail.com&loginpw=NXwr9U4oAZ&mode=iframe&referer=%2Fen%2Fstory%2Fcontents_list%2FDP000737%3F&sv_login=on'
    headers = {
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'iframe',
        'host': 'chinese.littlefox.com',
        'Cookie': 'cx0=veW0%2BHrvdG54Vjl%2By8hOPHakL7W0OjZpI7o5GcCVJ%2BmVaRwQyRJ72N3cFs4EQcdjHY6TrsddkvNhq%2Fkkbre0AA%3D%3D; cx1=9z6F%2B6B%2FqBCHH7akPUbD3T3hy7WtaeHuEkpQZsXQrrLTor5xXPBsM4xaRm5kPGYoptcgivwtpunsQm7WjKjFew%3D%3D; cx2=kFTRaU7xXyvXbhMFUE2hDdQ3E23zdrcQLCr6vBvsSWoz2GzhC5LU3EHFW6SWosHyskL40cGf0XhOodtyWb0t4A%3D%3D; cx4=c33RFGlniPckNyu4xl8Hl1GmJ5M0qEoguADFOzH4U8HASLB7iRvHlZEHXDdHn0xoxY50unyTif3z1ySPWrnACw%3D%3D; cx5=UA; cx6=4l52zgimVo7rc9QMbQGvtVzJs9x6fiTyabslFmAzCfUDW7zyZPsmfSqt9J%2B%2FPX5jw5ZoxZUWEov0sjsyOCHIVQ%3D%3D; cx7=5bTdi17B%2FcYx3xUweMYoSD7FrrBRhcgk7HNbzCqtLNQ3auL4FUBwKVnXww6lhzJUYe%2Fv%2FIG2Ncp1PoNZBloeBw%3D%3D; cx8=xIdrTAHzrLkwUHELOejkiAAV0a1pOglkTHjLlSfMFgUDOkaxCnPCElKAucVonP5JJECwBPnWI%2Bp%2BVAxu2ukN%2Fw%3D%3D; cxs=S5fJLAjIlMYYEwU8Cph8Rk1U9kp3ZsHMcPoVSHC1t0YIMksUw45V5HiRwptfNYF6XANW1nl3co8fAw%2BBmB8Biw%3D%3D; cxu=1; logged=t9KLGxOdTQL95NUjDulX6uBszQ9P7p4KtZ095cy%2FxlttjsIEFV7MvLoL%2FjZwC6W0UBN7LyEJ2zjWpOZgiv4DYg%3D%3D; sv_login=on; ci_session=91ae85613d9780f3a9ab3334338344c4b1f44046'
    }

    response = session.request("POST", url, headers=headers, data=payload)


# chapter_ids = ['C0003621', 'C0003622', 'C0003623', 'C0003624', 'C0003625', 'C0003626', 'C0003627', 'C0003628', 'C0003629', 'C0003630', 'C0003631', 'C0003632', 'C0003633', 'C0003634', 'C0003635', 'C0003636', 'C0003637', 'C0003638', 'C0003639', 'C0003640']
chapter_ids = ['C0003621']
# get_chapter_transcripts(chapter_ids, s)

# constants
story_id = "DP000754"
sleep_seconds = 3
if __name__ == '__main__':
    # setup requests session
    s = requests.Session()
    login(s)

    # get pages
    num_pages = get_table_of_contents_pages(story_id, s)

    # iterate through pages, collect chapters
    chapters = []
    for page in range(num_pages):
        chapters.append(get_chapter_ids_of_story(story_id, page))

    print(chapters)

    # todo uncomment this after coming home
    # todo you were working on getting all chapters of thumbelina
    # you finished getting all chapters in a page. now to increment pages after scraping
    # the chapters

    for chapter_id in chapters:
        chapter = chapter_to_text("chapter_id", s)
        save_and_append("thumbelina.txt", chapter)

    # get URLs of all stories
    # url = 'https://chinese.littlefox.com/en/story'  # Replace with the actual URL
    # urls = get_story_urls(url)
    #
    # output = {}
    #
    # # for each story, open it
    # for story_url, story_name in urls:
    #     num_pages = get_table_of_contents_pages(story_url, s)
    #     page_url = story_url
    #     for page in range(num_pages):
    #         # get text
    #         chapters = get_chapter_ids_of_story(url)
    #         for chapter in chapters:
    #             text = chapter_to_text(chapter, s)
    #
    #         page_url = get_next_page_url(page_url)
    #
    #     # for each chapter in table of contents, open each chapter
    #     # for page in story_url:
    #     #     get_chapter_transcripts(story_url)
    #
    #     time.sleep(sleep_seconds)

