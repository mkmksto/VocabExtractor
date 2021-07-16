# -*- coding: utf-8 -*-
# Copyright: Tanaka Aiko (https://github.com/aiko-tanaka)
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

# parts of the code are copied from renato's work (https://github.com/rgamici)

from io import StringIO
from html.parser import HTMLParser

import logging
import traceback

if False:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from anki.hooks import addHook
    from anki.notes import Note
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
sample2 = r"dasdasd<b>僕</b>dasdasdasdsa dasdsa dasdas dasdsadasdas"
# print(sample2.split("<b>")[1].split("</b>")[0])

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
    """Used to organize the work flow to update the selected cards
       Attributes
       ----------
       ed :
           Anki Card browser object
       fids :
           List of selected cards
       completed : int
           Track how many cards were already processed
       config : dict
           Stores the user's (customized) parameters

       Methods
       ------
       prepare()
           Check cards that have to be processed and create threads
           NOTE: the try/except block comes from the original code and it was
                 preserved to avoid unknown errors, it may be useless
       """
    def __init__(self, ed, fids):
        self.ed = ed
        self.fids = fids
        self.completed = 0
        # ed.selectedNotes
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

    def get_vocab(self, sentence):
        """return the bolded word from the sentence"""
        # return an empty string if sentence is empty
        return sentence.split("<b>")[1].split("</b>")[0] if sentence else ""

    def prepare(self):
        fs = [mw.col.getNote(id=fid) for fid in self.fids]
        i = 0
        for f in fs:
            try:
                if self.config['force_update'] == 'no' and f[definitionField]:
                    self.completed += 1
                    mw.progress.update(
                        label=label_progress_update,
                        value=self.completed)
                else:
                    # main shit that updates the vocab field
            except:
                print('definitions failed:')
                traceback.print_exc()



def setup_menu(ed):
    """Add entry in Edit menu"""
    a = QAction(label_menu, ed)
    a.triggered.connect(lambda _, e=ed: on_regen_vocab(e))
    ed.form.menuEdit.addAction(a)
    a.setShortcut(QKeySequence(keybinding))


def add_to_context_menu(view, menu):
    """Add entry to context menu (right click)"""
    menu.addSeparator()
    a = menu.addAction(label_menu)
    a.triggered.connect(lambda _, e=view: on_regen_vocab(e))
    a.setShortcut(QKeySequence(keybinding))


if False:
    def on_regen_vocab(ed):
        """main function"""
        regen = Regen(ed, ed.selectedNotes())
        regen.prepare()
        mw.requireReset()

    addHook('browser.setupMenus', setup_menu)
    addHook('browser.onContextMenu', add_to_context_menu)

