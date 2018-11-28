import random

import MySQLdb

def pseudo_query(query, wechat, category):
    data = ''
    conn = MySQLdb.connect(
        host='192.168.0.103',
        port=3306,
        user="root",
        passwd="cgll.123",
        db="price_system",
        charset="utf8"
    )
    try:
        cur = conn.cursor()
        if query == 1:
            sql = 'SELECT `desc` FROM pseudo_account WHERE wechat="{}" and category="{}";'\
                        .format(wechat, category)
        else:
            sql = 'SELECT `template` FROM pseudo_ad_template WHERE category="{category}";'\
                        .format(category=category)
        cur.execute(sql)
        data = cur.fetchall()
        data = random.choice(data)[0]
    finally:
        cur.close()
    conn.close()
    print('\033[93m 获取数据：{} \033[0m'.format(data))
    return data




if __name__ == '__main__':
    pseudo_query(2, '190265939', '手表')
