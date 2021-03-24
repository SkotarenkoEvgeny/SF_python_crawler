from os import path
from time import time
from io import BytesIO
from re import match

from cairosvg import svg2png
from requests_html import HTMLSession
from PIL import Image

session = HTMLSession()
start_time = time()

SAVING_DIR = 'output_dir'
IMAGE_TYPE_LIST = {'jpeg', 'png', 'webp', 'bmp', 'dib', 'esp', 'iso', 'tga', 'tiff'}

start_url = 'https://requests-html.kennethreitz.org'
# start_url = 'https://english-tutor-jeny797-2.herokuapp.com'
count = 1
image_saving_type = 'png'

visited_links_list = set()
visited_image_list = set()


def search_image_worker(url):

    global count
    r = session.get(url)
    # print(url)
    # print(r.status_code)
    if r.status_code != 200:
        return f'Staus code of {url} is {r.status_code}'

    page_links = set(r.html.absolute_links)
    page_images = set([i.attrs['src'] for i in r.html.xpath('//img')])

    not_visited_links = page_links.difference(visited_links_list)
    not_handled_images = page_images.difference(visited_image_list)

    for image_link in not_handled_images:
        print(image_link)
        image_link = image_link.split('?')[0]
        visited_image_list.add(image_link)

        # check the link is absolute or relative
        if not match(r'^(?:[a-z]+:)?\/\/', image_link):
            image_link = start_url + '/' + image_link
        print(image_link)

        # check image type
        download_image_type = image_link.split('.')[-1]
        if download_image_type not in IMAGE_TYPE_LIST:
            print(f"Image type {download_image_type} not suported.")
            continue

        if download_image_type == 'svg':
            print('SVG')
            svg2png(url=image_link, write_to=path.join(SAVING_DIR,f'image-{count}.{image_saving_type}'))
        image = session.get(image_link)
        content_type = image.headers['Content-Type'].split('/')[-1]

        # with Image.open(requests.get(image_link, stream=True).raw) as file:
        with Image.open(BytesIO(image.content)).convert("RGB") as file:
            file.save(path.join(SAVING_DIR,f'image-{count}.{image_saving_type}'))
        count +=1

    for page_link in not_visited_links:
        if match(start_url, page_link):
            visited_links_list.add(page_link)
            search_image_worker(page_link)

print(search_image_worker(start_url))
print(len(visited_links_list))
print(len(visited_image_list))
print(visited_image_list)
print((time() - start_time))


