import os
import re
from pathlib import Path

import sublime
import sublime_plugin

try:
    # I hate Python import system xd
    import sys
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    from .api import Shaman
except Exception:
    from api import Shaman

__version__ = "0.0.1"

CONTENT_PATH = None
TRANSLATED_CONTENT_PATH = None
LANG_CODE = None
ALERTS = None

cpath = str(Path("\\content"))
tcpath = str(Path("\\translated-content"))
uspath = str(Path("\\en-us"))

valid_exts = ('.md', '.html')
exts_dict = {'.md': '.html', '.html': '.md'}


def plugin_loaded():
    global CONTENT_PATH
    global TRANSLATED_CONTENT_PATH
    global LANG_CODE
    global ALERTS

    settings = sublime.load_settings('LionDocs.sublime-settings')
    CONTENT_PATH = settings.get('paths').get('content')
    TRANSLATED_CONTENT_PATH = settings.get('paths').get('translated-content')
    LANG_CODE = settings.get('lang_code')
    ALERTS = settings.get('alerts')

    checkConfig(CONTENT_PATH, TRANSLATED_CONTENT_PATH, LANG_CODE, ALERTS)


def alert(message: str) -> None:
    if ALERTS:
        sublime.message_dialog(message)
    else:
        print(message)


def checkConfig(*args) -> None:
    """
    Check plugin configuration and show a message if
    exist default (empty) values
    """
    err_count = 0
    for value in args:
        if value == "":
            err_count += 1

    if err_count > 0:
        print("Please check LionDocs configuration, you have {0} empty values".format(err_count))


def checkValidFile(file_path: str) -> bool:
    """
    Check if the received files is part of content or
    translated-content dirs
    """
    if CONTENT_PATH in file_path or TRANSLATED_CONTENT_PATH in file_path:
        return True
    return False


class getshaCommand(sublime_plugin.TextCommand):
    def __insert_in_cursor(self, edit, string):
        """
        Insert given string in current cursor position
        """
        self.view.insert(edit, self.view.sel()[0].begin(), string)

    def run(self, edit, mode):
        # TODO: Just work when function is called in a file
        # inside content or translated-content
        target_file = Path(self.view.file_name())

        if checkValidFile(str(target_file)):

            file_ext = target_file.suffix

            if file_ext in valid_exts:
                # replace translated-content with content
                tmp = str(target_file).replace(tcpath, cpath)

                # replace en-us with target language
                lang = str(Path("\\" + LANG_CODE))
                target_in_content = Path(tmp.replace(lang, uspath))

                meta = None

                if target_in_content.is_file():
                    shaman = Shaman(target_in_content, CONTENT_PATH)  # here?
                    meta = shaman.get_file_sha(returnas='meta')
                else:
                    # try switching extension for find target file
                    switch_ext = target_in_content.with_suffix(exts_dict[file_ext])
                    target_in_content = switch_ext

                    if target_in_content.is_file():
                        shaman = Shaman(target_in_content, CONTENT_PATH)
                        meta = shaman.get_file_sha(returnas='meta')
                    else:
                        # ??? File doesn't exist in content? Update content repo
                        # raise Exception('File does not exist in content?')
                        sublime.message_dialog("File does not exist in content?"
                                               " Please sync your forks")

                if mode == 'insert':
                    self.__insert_in_cursor(edit, meta)

                elif mode == 'clipboard':
                    sublime.set_clipboard(meta)

                    alert("SHA successfully copied to clipboard!")
        else:
            alert("File is not part of mdn directories!")


class transferCommand(sublime_plugin.TextCommand):
    def run(self, edit, mode):
        file_to_transfer = Path(self.view.file_name())  # file in content

        if checkValidFile(str(file_to_transfer)):
            # replace content with translated-content
            temp = str(file_to_transfer).replace(cpath, tcpath)

            # replace en-us with target language
            lang = str(Path("\\" + LANG_CODE))
            final_file_path = temp.replace(uspath, lang)

            # get final file dir tree
            dir_tree = str(Path(final_file_path).parent)

            # create dir tree if not exist
            if not os.path.exists(dir_tree):
                os.mkdir(dir_tree)

            # open original and destiny file at same time
            with open(str(file_to_transfer), 'r') as original_file, open(final_file_path, 'w') as final_file:
                original_content = original_file.read()

                if mode == 'same_file':
                    # Transfer exactly same file
                    final_file.write(original_content)

                    alert("File transfered successfully!")

                elif mode == 'with_sha':
                    # Transfer exactly same file but with sha commit
                    shaman = Shaman(file_to_transfer, CONTENT_PATH)
                    meta = shaman.get_file_sha(returnas='meta')

                    sep_index = [i.start() for i in re.finditer('---', original_content)][1]  # get separator index
                    final_content = original_content[:sep_index] + meta + "\n" + original_content[sep_index:]
                    final_file.write(final_content)

                    alert("File with sourceCommit transfered successfully!")

        else:
            alert("File is not part of mdn directories!")
