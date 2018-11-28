import re

SEPARATOR = '<br/><br/>'

def trim(line):
    return re.sub(r'(</p>|<br>|<p>|\d|\s|\r)', '', line)
