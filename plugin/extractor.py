# -*- coding: utf-8 -*-
# Copyright: Tanaka Aiko (https://github.com/aiko-tanaka)
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

# parts of the code are copied from renato's work (https://github.com/rgamici)

from io import StringIO
from html.parser import HTMLParser

if False:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from aqt import mw

# Variables controlled by the user (can be edited on Addons > Config)
config = mw.addonManager.getConfig(__name__)
expressionField = config['expressionField']
definitionField = config['definitionField']
keybinding = config['keybinding'] #nothing by default

# Labels
# text shown while processing cards
label_progress_update = 'Generating Japanese definitions...'
# text shown on menu to run the functions
label_menu = 'Extract Vocab wrapped in <b></b> from Sentence field'

sample_sentence = r"<ruby><rb>僕</rb><rt>ぼく</rt></ruby>に<ruby><rb>勝手" \
                  r"</rb><rt>かって</rt></ruby>に、<ruby><rb>人</rb><rt>ひと</rt></ruby>を<b><ruby><rb" \
                  r">裁</rb><rt>さば</rt></ruby>く</b><ruby><rb>権利</rb><rt>けんり</rt></ruby>があるのか？"

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

# if string/vocab is empty, do nothing

class Regen():
    def __init__(self, ed, fids):
        self.ed = ed
        self.fids = fids
        self.completed = 0
        self.config = mw.addonManager.getConfig(__name__)
        if len(self.fids) == 1:
            # Single card selected, need to deselect it before updating
            self.row = self.ed.currentRow()
            self.ed.form.tableView.selectionModel().clear()
        mw.progress.start(max=len(self.fids), immediate=True)
        mw.progress.update(
            label=label_progress_update,
            value=0)


def setupMenu(ed):
    """Add entry in Edit menu"""
    a = QAction(label_menu, ed)
    a.triggered.connect(lambda _, e=ed: onRegenGlosses(e))
    ed.form.menuEdit.addAction(a)
    a.setShortcut(QKeySequence(keybinding))


def addToContextMenu(view, menu):
    """Add entry to context menu (right click)"""
    menu.addSeparator()
    a = menu.addAction(label_menu)
    a.triggered.connect(lambda _, e=view: onRegenGlosses(e))
    a.setShortcut(QKeySequence(keybinding))


# def onRegenGlosses(ed):
#     """ """
#     regen = Regen(ed, ed.selectedNotes())
#     regen.prepare()
#     regen.wait_threads()
#     mw.requireReset()

