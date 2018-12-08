import re

SEPARATOR = '<br/><br/>'

def trim(line):
    return re.sub(r'(</p>|<br>|<p>|\s|\r|\d|微信|VX|卫星|威信|微芯|公众号|工棕号|关注|添加|薇信|唯芯|\+V|vx)', '', line)
