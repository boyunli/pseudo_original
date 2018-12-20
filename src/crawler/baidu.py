import random
from urllib.parse import quote
from lxml import etree

from utils.request_pkg import request_get as rget
from utils.comm import trim


class BaiDuCrawler:

    def main(self, title):
        keyword = title.split('，')[0]
        total_page = self._total_pages(keyword)
        pages = [i for i in range(0, total_page, 10)]
        page = random.choice(pages)
        param = self._crawl(keyword, page)
        while param == 0:
            pages.remove(page)
            if pages:
                page = random.choice(pages)
                param = self._crawl(keyword, page)
            else:
                param = ''
        print('\033[93m baidu:{}\n\033[0m'.format(param))
        return param

    def _total_pages(self, keyword):
        url = 'https://zhidao.baidu.com/search?ct=17&pn=0&tn=ikaslist&rn=10&fr=wwwt&word={}'.format(quote(keyword))
        resp = rget(url)
        html = etree.HTML(resp.text)
        pager = html.xpath('//a[@class="pager-last"]/@href')
        if pager:
            # 百度知道页数规律 10n = page (n>=0)
            page = int(pager[0].split('pn=')[-1])
        else:
            page = range(0, 100, 10)
            page = 100
        return page

    def _crawl(self, keyword, page):
        url = 'https://zhidao.baidu.com/search?ct=17&pn={page}&tn=ikaslist&rn=10&fr=wwwt&word={word}'\
            .format(word=quote(keyword), page=page)
        resp = rget(url)
        html = etree.HTML(resp.text)
        hrefs = html.xpath('//div[@class="list-inner"]/div/dl/dt/a/@href')

        href = ''
        answers = []
        while not answers:
            if not hrefs:
                return 0
            href = random.choice(hrefs)
            hrefs.remove(href)
            href_resp = rget(href)
            href_html = etree.HTML(href_resp.content.decode('gbk', 'ignore'))
            content = href_html.xpath('//div[@class="line content"]')
            articles = [''.join(a.xpath('.//p/text()')) for a in content]
            # 选出 回答超过200 字的
            answers = [a for a in articles if len(trim(a))>=200]
        print("\033[94m 百度知道爬取第{}页，爬取URL:{}; \033[0m".format(page, href))

        answer = random.choice(answers)
        answer_length = len(answer)
        params = answer.split('。')
        params_length = len(params)
        # 需要截取的问答段落数
        cut_nums = 200//(answer_length//params_length)
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

        return trim(param)


if __name__ == '__main__':
    title = '阿玛尼手表，一比一工厂货源直销'
    BaiDuCrawler().main(title)
