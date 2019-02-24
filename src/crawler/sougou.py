import re
import random
from lxml import etree
import json

import brotli

from utils.request_pkg import request_get as rget
from utils.comm import trim, SEPARATOR as separator

class SougouCrawler:

    def __init__(self):
        pass

    def main(self, title):
        keyword = title.split('，')[0]
        weixin_total_page = self._crawl_weixin_total_page(keyword)
        weixin_pages = [i for i in range(weixin_total_page)]
        weixin_page = random.choice(weixin_pages)
        weixin_param = self._crawl_weixin(keyword, weixin_page)
        while weixin_param == 0:
            weixin_pages.remove(weixin_page)
            if weixin_pages:
                weixin_page = random.choice(weixin_pages)
                weixin_param = self._crawl_weixin(keyword, weixin_page)
            else:
                weixin_param = ''

        zhihu_total_page = self._crawl_zhihu_total_page(keyword)
        zhihu_pages = [i for i in range(zhihu_total_page)]
        zhihu_page = random.choice(zhihu_pages)
        zhihu_param = self._crawl_zhihu(keyword, zhihu_page)
        while zhihu_param == 0:
            zhihu_pages.remove(zhihu_page)
            if zhihu_pages:
                zhihu_page = random.choice(zhihu_pages)
                zhihu_param = self._crawl_zhihu(keyword, zhihu_page)
            else:
                zhihu_param = ''

        print('\033[93m weixin:{}\n\n zhihu:{}\033[0m'.format(weixin_param, zhihu_param))
        return separator.join([zhihu_param, weixin_param])

    def _crawl_weixin_total_page(self, keyword):
        url = 'https://weixin.sogou.com/weixinwap?page={page}&_rtype=json&query={keyword}&type=2&ie=utf8&_sug_=y&_sug_type_=&s_from=input&'\
            .format(keyword=keyword, page=1)
        resp = rget(url)
        total_page = re.findall(r'"totalPages":(\d+),', resp.text)
        total_page = int(total_page[0]) if total_page else 3
        return total_page

    def _crawl_weixin(self, keyword, page):
        url = 'https://weixin.sogou.com/weixinwap?page={page}&_rtype=json&query={keyword}&type=2&ie=utf8&_sug_=y&_sug_type_=&s_from=input&'\
            .format(keyword=keyword, page=page)
        resp = rget(url)
        hrefs = re.findall(r'<encArticleUrl><!\[CDATA\[(.*?)]]', resp.text)

        href = ''
        article = ''
        article_length = 0
        while article_length < 200:
            if not hrefs:
                return 0
            href = random.choice(hrefs)
            hrefs.remove(href)
            href_resp = rget(href)
            html = etree.HTML(href_resp.content)
            params = html.xpath('//*[@id="js_content"]/descendant::*/text()')
            article = trim(''.join(params))
            article_length = len(article)
        print("\033[94m 搜狗微信爬取第{}页，爬取URL:{}; 获取文章字数：{}. \033[0m".format(page, href, article_length))

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

    def _crawl_zhihu_total_page(self, keyword):
        url = 'https://zhihu.sogou.com/websearch/zhihu/sogou_ajax.jsp?query={keyword}&_sug_type_=&_rtype=json&s_from=input&_sug_=y&type=2&ie=utf8&from=ajax&page={page}&resultMode=0'\
            .format(keyword=keyword, page=1)
        resp = rget(url)
        total_page = re.findall(r'(\d+),1,.*\[PAGE_INFO\]', resp.text)
        total_page = int(total_page[0]) if total_page else 3
        return total_page

    def _crawl_zhihu(self, keyword, page):
        url = 'https://zhihu.sogou.com/websearch/zhihu/sogou_ajax.jsp?query={keyword}&_sug_type_=&_rtype=json&s_from=input&_sug_=y&type=2&ie=utf8&from=ajax&page={page}&resultMode=0'\
            .format(keyword=keyword, page=page)
        resp = rget(url)
        html = etree.HTML(resp.text)
        if not html:
            return 0
        hrefs = html.xpath('//li/a/@href')

        href = ''
        param = ''
        article_length = 0
        param_num = 3
        while article_length < 200:
            if not hrefs:
                return 0
            href = random.choice(hrefs)
            hrefs.remove(href)
            if '/question/' in href:
                # 知乎问答页
                article_id = re.findall(r'/(\d+)[/#]answer', href)
                if not article_id: continue
                href_ = 'https://www.zhihu.com/api/v4/questions/{article_id}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=20&offset=&sort_by=default'\
                    .format(article_id=article_id[0])
                href_resp = rget(href_)
                if href_resp.headers.get('Content-Encoding') == 'br':
                    data = brotli.decompress(href_resp.content).decode('utf-8')
                    try:
                        jdata = json.loads(data)
                    except json.decoder.JSONDecodeError:
                        continue
                    article = [answer['content'].split('<figure>')[0] for answer in jdata['data']]
                    # 选出 回答超过200 字的
                    params = [p for p in article if len(trim(p))>=200]
                    if not params: continue
                    param = trim(random.choice(params))
                    article_length = len(param)
            else:
                # 知乎文章页 '/p' in href
                href_resp = rget(href)
                if href_resp.headers['Content-Encoding'] == 'br':
                    data = brotli.decompress(href_resp.content).decode('utf-8')
                    html = etree.HTML(data)
                    params = html.xpath('//p/text()')
                    param_num += 1
                    if param_num > len(params):
                        param_num = len(params)
                    param = trim(''.join(random.sample(params, param_num)))
                    article_length = len(param)
        print("\033[94m 搜狗知乎爬取第{}页，爬取URL:{}; 获取文章字数：{}. \033[0m".format(page, href, article_length))
        return param



if __name__ == '__main__':
    title = '阿玛尼手表，一比一工厂货源直销'
    SougouCrawler().main(title)
