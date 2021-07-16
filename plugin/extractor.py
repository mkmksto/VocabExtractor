# -*- coding: utf-8 -*-
# Copyright: Tanaka Aiko (https://github.com/aiko-tanaka)
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

from io import StringIO
from html.parser import HTMLParser

# https://stackoverflow.com/questions/2081640/what-exactly-do-u-and-r-string-flags-do-and-what-are-raw-string-literals
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# text = r"<ruby><rb>僕</rb><rt>ぼく</rt></ruby>は<ruby><rb>最初</rb><rt>さいしょ</rt></ruby>から<ruby><rb>危険</rb><rt>きけん</rt></ruby>を<b><ruby><rb>犯</rb><rt>おか</rt></ruby>している</b>じゃないか、"
# print(strip_tags(text))

