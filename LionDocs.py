import os
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

CONTENT = None
TRANSLATED_CONTENT = None
LANG_CODE = None
valid_exts = ('.md', '.html')
exts_dict = {'.md': '.html', '.html': '.md'}


def plugin_loaded():
    global CONTENT
    global TRANSLATED_CONTENT
    global LANG_CODE
    settings = sublime.load_settings('LionDocs.sublime-settings')
    CONTENT = settings.get('paths').get('content')
    TRANSLATED_CONTENT = settings.get('paths').get('translated-content')
    LANG_CODE = settings.get('lang_code')


class getshaCommand(sublime_plugin.TextCommand):
    def __insert_in_cursor(self, edit, string):
        """
        Insert given string in current cursor position
        """
        self.view.insert(edit, self.view.sel()[0].begin(), string)

    def run(self, edit, mode):
        # TODO: Just act in files inside content or translated content
        target_file = Path(self.view.file_name())
        file_ext = target_file.suffix

        if file_ext in valid_exts:
            tmp = str(target_file).replace("translated-content", "content")
            lang = "\\" + LANG_CODE + "\\"
            target_in_content = Path(tmp.replace(lang, "\\en-us\\"))

            meta = None

            if target_in_content.is_file():
                shaman = Shaman(target_in_content, CONTENT)  # here?
                meta = shaman.get_file_sha(returnas='meta')
            else:
                switch_ext = target_in_content.with_suffix(exts_dict[file_ext])
                target_in_content = switch_ext

                if target_in_content.is_file():
                    shaman = Shaman(target_in_content, CONTENT)
                    meta = shaman.get_file_sha(returnas='meta')
                else:
                    # ??? File doesn't exist in content? Update content repo
                    raise Exception('File does not exist in content?')

            if mode == 'insert':
                self.__insert_in_cursor(edit, meta)
            elif mode == 'clipboard':
                sublime.message_dialog("TODO :)")


class transferCommand(sublime_plugin.TextCommand):
    def run(self, edit, mode):
        target_file = Path(self.view.file_name())

        rpl1 = str(target_file).replace("\\content\\", "\\translated-content\\")
        rpl2 = str(rpl1).replace("\\en-us\\", "\\" + LANG_CODE + "\\")
        # print(LANG_CODE)
        dir_tree = str(Path(rpl2).parent)

        if not os.path.exists(dir_tree):
            os.mkdir(dir_tree)

        if mode == 'same_file':
            with open(str(target_file), 'r') as to_read, open(rpl2, 'w') as to_write:
                content = to_read.read()
                to_write.write(content)

            sublime.message_dialog("File transfered successfully!")

        elif mode == 'with_sha':
            sublime.message_dialog("TODO :)")
