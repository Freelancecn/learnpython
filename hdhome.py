#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import logging
import requests
import pytesseract
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup

logging.basicConfig(filename='hdhome.log',filemode='a',level=logging.INFO,format='%(asctime)s - %(message)s',datefmt='%d-%b-%y %H:%M:%S')

class PreImage(object):

    def __init__(self,image):
        self.image = Image.open(image).convert('L')

    def image_to_bin(self,threshold=120):
        pixdata = self.image.load()
        w, h = self.image.size
        for y in range(h):
            for x in range(w):
                if pixdata[x, y] < threshold:
                    pixdata[x, y] = 0
                else:
                    pixdata[x, y] = 255
        self.image.save('temp.png')
        return self.image

    def delete_point(self):
        pixdata = self.image.load()
        w,h = self.image.size
        for y in range(1,h-1):
            for x in range(1,w-1):
                count = 0
                if pixdata[x,y-1] > 245:
                    count = count + 1
                if pixdata[x,y+1] > 245:
                    count = count + 1
                if pixdata[x-1,y] > 245:
                    count = count + 1
                if pixdata[x+1,y] > 245:
                    count = count + 1
                if pixdata[x-1,y-1] > 245:
                    count = count + 1
                if pixdata[x-1,y+1] > 245:
                    count = count + 1
                if pixdata[x+1,y-1] > 245:
                    count = count + 1
                if pixdata[x+1,y+1] > 245:
                    count = count + 1
                if count > 6:
                    pixdata[x,y] = 255
        self.image.save('temp.png')
        return self.image

    def to_string(self):

        regex = r"[\W\_]"

        image = self.image_to_bin()
        image = self.delete_point()
        imagestring = pytesseract.image_to_string(image)
        imagestring = re.sub(regex,'',imagestring)
        return imagestring


class HDHome(object):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"

    def __init__(self,user_agent=user_agent,):
        self.session = requests.Session()
        self.session.headers.update({'user-agent':user_agent})
        self.session.headers.update({'origin':'https://hdhome.org'})
        self.session.headers.update({'referer':'https://hdhome.org/login.php'})

    def login(self,username,password,captcha,url='https://hdhome.org/takelogin.php'):
        imagestring = captcha[0]
        imagehash = captcha[1]
        playload = {'username':username,
                    'password':password,
                    'imagestring':imagestring,
                    'imagehash':imagehash}
        logging.info(len(imagestring))
        r = self.session.post(url,playload,timeout=5)
        logging.info('imagestring: {}'.format(imagestring))
        logging.info('imagehash: {}'.format(imagehash))
        logging.info('get {} code {}'.format(url,str(r.status_code)))
        return self.is_logged_in()


    def _get_login_captcha(self):
        url = 'https://hdhome.org/login.php'
        r = self.session.get(url,timeout=5)
        soup = BeautifulSoup(r.text,"html.parser")

        img = soup.find_all("img")
        for i in img:
            if 'image' in i['src']:
                imgurl = 'https://hdhome.org/' + i['src']
        image = self.session.get(imgurl)
        with open('/movie/captcha.png','wb') as f:
            f.write(image.content)
        image = BytesIO(image.content)
        image = PreImage(image)
        imagestring = image.to_string()

        imagehash = soup.find("input",{"name":"imagehash"})
        assert imagehash and imagehash['value'],"there is no imagehash on this page"

        return (imagestring,imagehash['value'])

    def is_logged_in(self,url='https://hdhome.org/index.php'):
        r = self.session.get(url)
        return 'Pls keep seeding' in r.text

    def sign(self):
        url = 'https://hdhome.org/attendance.php'
        self.session.headers.update({'referer':'https://hdhome.org/index.php'})
        self.session.headers.update({'upgrade-insecure-requests':'1'})
        r = self.session.get(url,allow_redirects=False)
        logging.info('get {} code {}'.format(url,str(r.status_code)))
        return r

def main():
    import time
    from random import randrange
    username = 'hdhome'
    password = 'hdhome'
    hdh = HDHome()
    times = 1
    while times < 8:
        captcha = hdh._get_login_captcha()
        if len(captcha[0]) == 6:
            time.sleep(randrange(5))
            logging.info('{} times trying'.format(times))
            hdh.login(username,password,captcha)
            times += 1
            time.sleep(randrange(5))
            r = hdh.sign()
            if r.status_code == 200:
                logging.info('sign success')
                break
            else:
                logging.info('sign failure')
                continue

if __name__ == '__main__':
    main()
