from os import path, mkdir
from time import time
from io import BytesIO
from re import match

from cairosvg import svg2png
from requests_html import HTMLSession
from PIL import Image, UnidentifiedImageError
from requests.exceptions import SSLError

SAVING_DIR = 'output_dir'
IMAGE_TYPE_LIST = {'jpeg', 'png', 'webp', 'bmp', 'dib', 'esp', 'iso', 'tga', 'tiff', 'svg', 'jpg'}

count = 1
image_saving_type = 'png'

visited_links_list = set()
visited_image_list = set()


def search_image_worker(url):
    global count
    try:
        r = session.get(url)
    except SSLError:
        return 'SSL access error'

    if r.status_code != 200:
        return f'Status code of {url} is {r.status_code}'

    page_links = set(r.html.absolute_links)
    not_visited_links = page_links.difference(visited_links_list)
    visited_links_list.update(not_visited_links)

    temp_image_list = r.html.xpath('//img')
    if len(temp_image_list) > 0:
        page_images = set([i.attrs['src'] for i in temp_image_list])
        not_handled_images = page_images.difference(visited_image_list)
        print(f'not_handled_images {len(not_handled_images)}')
        for image_link in not_handled_images:
            visited_image_list.add(image_link)
            image_link = image_link.strip()

            # check the link is absolute or relative
            if match(r'^(?:[a-z]+:)?\/\/', image_link) is None:
                image_link = start_url + '/' + image_link

            try:
                image = session.get(image_link)
            except SSLError:
                print('SSL access error')
                continue
            if image.status_code == 404:
                print(f'{image_link} {image.status_code}')
                continue

            # check image type
            download_image_type = image_link.split('.')[-1]
            if download_image_type == 'svg':
                print('SVG')
                svg2png(url=image_link, write_to=path.join(SAVING_DIR, f'image-{count}.{image_saving_type}'))
            else:
                try:
                    with Image.open(BytesIO(image.content)).convert("RGB") as file:
                        file.save(path.join(SAVING_DIR, f'image-{count}.{image_saving_type}'))
                except UnidentifiedImageError:
                    print(f"Can't handle image {image_link}")
            count += 1

    print(f'not_visited_links {len(not_visited_links)}')
    print("page count", len(visited_links_list))

    for page_link in not_visited_links:

        if match(start_url, page_link):
            if page_link.split('/')[-1] == 'captcha':
                continue
            search_image_worker(page_link)


if __name__ == '__main__':
    session = HTMLSession()
    start_time = time()
    if not path.exists(SAVING_DIR):
        mkdir(SAVING_DIR)

    start_url = input('Insert site url for crawling ')
    search_image_worker(start_url)

    print('crawling process is complete')
    print(f'Amount of visited links {len(visited_links_list)}')
    print(f'Amount of visited images links {len(visited_image_list)}')

    print(f'Work time is {(time() - start_time)}')
