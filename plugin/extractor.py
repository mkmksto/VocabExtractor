# -*- coding: utf-8 -*-
# Copyright: Tanaka Aiko (https://github.com/aiko-tanaka)
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

# parts of the code are copied from renato's work (https://github.com/rgamici)

# Note to self: I use if False: because I haven't cloned the Anki repo yet
# so pycharm doesn't recofnize aqt, anki, etc.

from io import StringIO
from html.parser import HTMLParser

import traceback
import os

test_in_anki = True

dir_path = os.path.dirname(os.path.realpath(__file__)).split("\\")[-1]
# print(dir_path)

if test_in_anki:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from anki.hooks import addHook
    from anki.notes import Note
    from aqt import mw

    # Variables controlled by the user (can be edited on Addons > Config)
    # dir_path = os.path.dirname(os.path.realpath(__file__)).split(r"\"")[-1]
    # print(dir_path)
    config = mw.addonManager.getConfig(dir_path)
    try:
        expression_field = config['expressionField']
        vocab_field = config['vocabField']
        keybinding = config['keybinding'] #nothing by default
    except:
        expression_field = "Expression"
        vocab_field = "Vocab"
        keybinding = ""  # nothing by default
        force_update = "no"

# text shown while processing cards
label_progress_update = 'Generating Japanese definitions...'
# text shown on menu to run the functions
label_menu = 'Extract Vocab wrapped in <b></b> from Sentence field'

# https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
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
        # ed.selectedNotes
        self.completed = 0
        self.config = mw.addonManager.getConfig(__name__)
        # self.sema = threading.BoundedSemaphore(config['max_threads'])
        # self.values = {}
        if len(self.fids) == 1:
            # Single card selected, need to deselect it before updating
            self.row = self.ed.currentRow()
            self.ed.form.tableView.selectionModel().clear()
        mw.progress.start(max=len(self.fids), immediate=True)
        mw.progress.update(
            label=label_progress_update,
            value=0)

    def _get_vocab_(self, sentence):
        """
        return the bolded word from the sentence
        """
        # return an empty string if sentence is empty
        # return an HTML-stripped vocab just to be sure an clean
        return strip_tags(sentence.split("<b>")[1].split("</b>")[0]) if sentence else ""

    def _update_progress(self):
        self.completed += 1
        mw.progress.update(
            label=label_progress_update,
            value=self.completed)

    def generate(self):
        fs = [mw.col.getNote(id=fid) for fid in self.fids]
        for f in fs:
            try:
                # vocab field already contains something
                if force_update == 'no' and f[vocab_field]:
                    self._update_progress()

                elif not f[vocab_field]:
                    # vocab_field is empty
                    f[vocab_field] += self._get_vocab_(f[expression_field])
                    self._update_progress()

                elif force_update == 'yes' and f[vocab_field]:
                    f[vocab_field] += self._get_vocab_(f[expression_field])
                    self._update_progress()

                else:
                    pass
            except:
                print('definitions failed:')
                traceback.print_exc()

def setup_menu(ed):
    """
    Add entry in Edit menu
    """
    a = QAction(label_menu, ed)
    a.triggered.connect(lambda _, e=ed: on_regen_vocab(e))
    ed.form.menuEdit.addAction(a)
    a.setShortcut(QKeySequence(keybinding))


def add_to_context_menu(view, menu):
    """
    Add entry to context menu (right click)
    """
    menu.addSeparator()
    a = menu.addAction(label_menu)
    a.triggered.connect(lambda _, e=view: on_regen_vocab(e))
    a.setShortcut(QKeySequence(keybinding))


def on_regen_vocab(ed):
    """
    main function
    """
    regen = Regen(ed, ed.selectedNotes())
    regen.generate()
    mw.requireReset()

addHook('browser.setupMenus', setup_menu)
addHook('browser.onContextMenu', add_to_context_menu)