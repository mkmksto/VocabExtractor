# -*- coding: utf-8 -*-
# Copyright: Tanaka Aiko (https://github.com/aiko-tanaka)
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

# parts of the code are copied from renato's work (https://github.com/rgamici)
# Description: Just a stupidly simple program that extracts a word wrapped in <b></b>
# and puts it into a dst field, yeah I'm lazy

# Note to self: I use if False: because I haven't cloned the Anki repo yet
# so pycharm doesn't recognize aqt, anki, etc.

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

## TO DO's
# fix how anki can't fucking find the config file
# understand what mw.progress.finish() does
# try actually catching errors from try: f.flush()
# handle cases where the sentence is empty

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

def get_vocab(sentence):
    """
    return the bolded word from the sentence
    """
    # return an empty string if sentence is empty
    # return an HTML-stripped vocab just to be sure an clean
    try:
        sentence = str(sentence)
        if sentence != "" and len(sentence.split("<b>")) == 2:
            return strip_tags(sentence.split("<b>")[1].split("</b>")[0])
        elif sentence == "":
            return ""
    except:
        raise

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
       """
    def __init__(self, ed, fids):
        self.ed = ed
        # ed.selectedNotes
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

    def _update_progress(self):
        self.completed += 1
        mw.progress.update(
            label=label_progress_update,
            value=self.completed)
        if self.completed >= len(self.fids):
            mw.progress.finish()
            return

    def generate(self):
        fs = [mw.col.getNote(id=fid) for fid in self.fids]
        for f in fs:
            # empty sentence field (probably very rare)
            if not f[expression_field]:
                continue

            try:
                # vocab field already contains something
                if force_update == 'no' and f[vocab_field]:
                    # do nothing, count it as progress
                    self._update_progress()
                    mw.progress.finish()
                    continue

                elif not f[vocab_field] and r"<b>" in str(f[expression_field]):
                    # vocab_field is empty, fill it
                    f[vocab_field] = get_vocab(f[expression_field])

                    self._update_progress()
                    mw.progress.finish()

                elif force_update == 'yes' and f[vocab_field] and r"<b>" in str(f[expression_field]):
                    f[vocab_field] += get_vocab(f[expression_field])

                    self._update_progress()
                    mw.progress.finish()

                else:
                    pass
            except:
                print('definitions failed:')
                raise
                # traceback.print_exc()

            try:
                f.flush()
            except:
                pass

            # just a fail-safe
            if self.completed >= len(self.fids):
                mw.progress.finish()
                return

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
    mw.reset()
    mw.requireReset()

addHook('browser.setupMenus', setup_menu)
addHook('browser.onContextMenu', add_to_context_menu)
