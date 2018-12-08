import sys
sys.path.append("/home/lily/py3/pseudo_original/src")
from flask import Flask, request, render_template, jsonify

from dashboard.db import pseudo_query
from utils.comm import SEPARATOR as separator
from crawler.baidu import BaiDuCrawler
from crawler.toutiao import TouTiaoCrawler
from crawler.sougou import SougouCrawler

app = Flask(__name__)
@app.route('/')
def index():
    wechats = [
        '2533651272',
        '190265939',
        '515550681',
        '774988330'
    ]
    categorys = [
        '手表',
        '包包'
    ]
    return render_template('index.html', wechats=wechats, categorys=categorys)


@app.route('/search', methods=['POST'])
def article_generator():
    # import pdb;pdb.set_trace()
    title = request.json.get('keyword')
    wechat = request.json.get('wechat')
    category = request.json.get('category')
    print("\033[95m title:{}; wecht:{}; category:{}\033[0m".format(title, wechat, category))

    # 获取文章第一段
    first = title + '。' + pseudo_query(1, wechat, category)
    second = pseudo_query(2, wechat, category)
    third = TouTiaoCrawler().main(title)
    fourth = BaiDuCrawler().main(title)
    fifth = SougouCrawler().main(title)
    content = separator.join([first, second, third, fourth, fifth])
    print("\033[95m content:{}\033[0m".format(content))


    data = [
        {'title': title, 'tag': category, 'content': content},
    ]
    return jsonify(data)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port='30004', debug=True)
