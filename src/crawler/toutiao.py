import re
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
        url = 'http://m.toutiao.com/search/content/?aid=1455&count=10&format=json&from=search_tab&source=&pd=synthesis&keyword={keyword}&keyword_type=&action_type=&from_search_subtab=&offset={offset}&has_count={offset}&qc_query='\
            .format(offset=page*20, keyword=quote(keyword))
        resp = rget(url)
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
    title = '阿玛尼ar2498手表价格，广州站西一件代发'
    TouTiaoCrawler().main(title)
