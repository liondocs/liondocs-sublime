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


def iPath(path, parent=False):
    """
    Receive path string, convert to system path and
    return path as string
    """
    if parent:
        return str(Path(path).parent)
    return str(Path(path))


__version__ = "0.1.0"

CONTENT_PATH = None
TRANSLATED_CONTENT_PATH = None
LANG_CODE = None
ALERTS = None

cpath = iPath("\\content")
tcpath = iPath("\\translated-content")
uspath = iPath("\\en-us")

valid_exts = ('.md', '.html')
exts_dict = {'.md': '.html', '.html': '.md'}


def validateFile(func):
    """
    Decorator for validate incoming file
    """

    def wrapper(self, edit, mode):
        file_path = iPath(self.view.file_name())

        if CONTENT_PATH in file_path or TRANSLATED_CONTENT_PATH in file_path:
            func(self, edit, mode)
        else:
            alert("File is not part of mdn directories!")
    return wrapper


def validateConfig(func):
    """
    Decorator for validate plugin config
    """

    def wrapper(self, edit, mode):
        configs = [CONTENT_PATH, TRANSLATED_CONTENT_PATH, LANG_CODE, ALERTS]
        err_count = 0
        for value in configs:
            if value == "":
                err_count += 1

        if err_count > 0:
            alert("Please check LionDocs configuration, you have {0} empty values".format(err_count))
        else:
            func(self, edit, mode)
    return wrapper


def alert(message: str) -> None:
    if ALERTS:
        sublime.message_dialog(message)
    else:
        print(message)


def plugin_loaded():
    try:
        global CONTENT_PATH
        global TRANSLATED_CONTENT_PATH
        global LANG_CODE
        global ALERTS

        settings = sublime.load_settings('LionDocs.sublime-settings')
        CONTENT_PATH = iPath(settings.get('paths').get('content'))
        TRANSLATED_CONTENT_PATH = iPath(settings.get('paths').get('translated-content'))
        LANG_CODE = settings.get('lang_code')
        ALERTS = settings.get('alerts')
    except AttributeError:
        # Error at plugin first load (and editor first load) by empty config
        pass


class getshaCommand(sublime_plugin.TextCommand):
    def __insert_in_cursor(self, edit, string):
        """
        Insert given string in current cursor position
        """
        self.view.insert(edit, self.view.sel()[0].begin(), string)

    @validateFile
    @validateConfig
    def run(self, edit, mode):
        target_file = Path(self.view.file_name())
        file_ext = target_file.suffix

        if file_ext in valid_exts:
            # replace translated-content with content
            tmp = str(target_file).replace(tcpath, cpath)

            # replace en-us with target language
            lang = iPath("\\" + LANG_CODE)
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
                    alert("File does not exist in content?"
                          " Please sync your forks")

            if mode == 'insert':
                self.__insert_in_cursor(edit, meta)

            elif mode == 'clipboard':
                sublime.set_clipboard(meta)

                alert("SHA successfully copied to clipboard!")


class transferCommand(sublime_plugin.TextCommand):
    @validateFile
    @validateConfig
    def run(self, edit, mode):
        file_to_transfer = Path(self.view.file_name())

        # replace content with translated-content
        temp = str(file_to_transfer).replace(cpath, tcpath)

        # replace en-us with target language
        lang = iPath("\\" + LANG_CODE)
        final_file_path = temp.replace(uspath, lang)

        # get final file dir tree
        dir_tree = iPath(final_file_path, parent=True)

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
