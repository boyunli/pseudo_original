import re
import time
import random
import json
from urllib.parse import quote

from utils.request_pkg import request_get as rget
from utils.comm import trim


class TouTiaoCrawler:

    def main(self, title):
        keyword = title.split('，')[0]
        pages = [i for i in range(5)]
        page = random.choice(pages)
        param = self._crawl(keyword, page)
        while param == 0:
            pages.remove(page)
            if pages:
                page = random.choice(pages)
                param = self._crawl(keyword, page)
            else:
                param = ''
        print('\033[93m toutiao:{}\n\033[0m'.format(param))
        return param

    def _crawl(self, keyword, page):
        cookies = {"uuid": "\"w:1bd17d69c10f4782b52accf8f6006ef5\"", "login_flag": "a767ab2a7a49e910f3b9700d98d412a1", "CNZZDATA1259612802": "1079077849-1543464987-%7C1556332764", "sid_guard": "\"2a6b2e47f06891df152d8425359a457b|1556334609|15552000|Thu\\054 24-Oct-2019 03:10:09 GMT\"", "s_v_web_id": "d8f7978cf72c6b7a216b1392985125d0", "passport_auth_status": "3e121590113b3d7aad18af0235ad1e4a", "WEATHER_CITY": "%E5%8C%97%E4%BA%AC", "tt_webid": "6629131804900017678", "UM_distinctid": "1675daf3f4b253-06b3411d4fbc8e-8383268-e1000-1675daf3f4d8f", "sessionid": "2a6b2e47f06891df152d8425359a457b", "csrftoken": "ab4ca442ba52027f6b5369f2418ae526", "sid_tt": "2a6b2e47f06891df152d8425359a457b", "__tasessionId": "5fnd6dsvo1556334592167", "uid_tt": "73f3c75ace4ab1d26218a9a83c050745", "sso_uid_tt": "2864a8d0f78e512f8cbd0e921c6fb286", "toutiao_sso_user": "cd44704a659973f5e7c746a6e20ba302"}
        url = 'https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset={offset}&format=json&keyword={keyword}&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp={timestamp}'\
            .format(offset=page*20, keyword=quote(keyword), timestamp=int(time.time()*1000))
        resp = rget(url, cookies)
        data = json.loads(resp.text)
        # 只爬取今日头条的文章，由今日头条 跳转到别的平台的不爬取
        hrefs = [ article['article_url'] for article  in data['data']
                 if article.get('article_url') and not article.get('display')
                 and 'toutiao' in article.get('article_url') ]

        href = ''
        article = ''
        article_length = 0
        num = 0
        while article_length < 200 and num < 3:
            if not hrefs:
                return ''
            href = random.choice(hrefs)
            hrefs.remove(href)
            href_resp = rget(href)
            article = ''.join(re.findall(r"content: '(.+)'?", href_resp.text))
            article = trim(article)
            article = re.sub('[&lt&gt&quot;pa-z\/#3D\.-:_\-{}%|(a-zA-Z{6})]', '', article)
            article_length = len(article)
            num += 1
        print("\033[94m 今日头条爬取第{}页，爬取URL:{}; 获取文章字数：{}. \033[0m".format(page, href, article_length))

        params = article.split('。')
        params_length = len(params)
        # 需要截取的文章段落数
        cut_nums = 200//(article_length//params_length)
        param_count = 0
        param = ''
        while param_count < 200:
            cut_nums += 1
            if cut_nums >= params_length:
                cut_nums = params_length - 1
                param = ''.join(random.sample(params, cut_nums))
                break
            param = ''.join(random.sample(params, cut_nums))
            param_count = len(param)
        if param:
            param = param if param.endswith('。') else param + '。'
        return param



if __name__ == '__main__':
    title = '理查德米勒黑骷髅头，一比一复刻站西工厂货源'
    TouTiaoCrawler().main(title)
