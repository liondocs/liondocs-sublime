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


__version__ = "0.1.1"

cpath = os.path.sep + "content"
tcpath = os.path.sep + "translated-content"
uspath = os.path.sep + "en-us"

valid_exts = ('.md', '.html')
exts_dict = {'.md': '.html', '.html': '.md'}


def ipath(path: str, parent: bool = False) -> str:
    """
    Receive path string, convert to system path and return path as string
    """
    if parent:
        return str(Path(path).parent)
    return str(Path(path))


def echo(mode: str, message: str) -> None:
    """
    Log function for track plugin internal progress
    """
    mode = "[{}]".format(mode.ljust(8))
    print(mode, message)


class Config:
    def __init__(self):
        super(Config, self).__init__()
        self.__settings = sublime.load_settings('LionDocs.sublime-settings')
        self.content = ipath(self.__settings.get('paths').get('content'))
        self.translated_content = ipath(self.__settings.get('paths').get('translated-content'))
        self.lang_code = self.__settings.get('lang_code')
        self.alerts = self.__settings.get('alerts')
        self.__configs = [self.content, self.translated_content, self.lang_code, self.alerts]

    def isValid(self):

        err_count = 0
        for value in self.__configs:
            if value == "":
                err_count += 1

        return True if err_count == 0 else False


def validateFile(func):
    """
    Decorator for validate incoming file
    """

    def wrapper(self, edit, mode):
        file_path = ipath(self.view.file_name())
        config = Config()

        if config.content in file_path or config.translated_content in file_path:
            echo("VALIDATE", "Selected file is valid")
            func(self, edit, mode)
        else:
            echo("VALIDATE", "Selected file is not part of setted directories")
            alert("File is not part of mdn directories!")
    return wrapper


def validateConfig(func):
    """
    Decorator for validate plugin config
    """

    def wrapper(self, edit, mode):
        plugin_config = Config()

        if plugin_config.isValid():
            echo("CONFIG", "Configuration parameters are valid")
            func(self, edit, mode)
        else:
            echo("CONFIG", "Configuration parameters are not valid, please check")
            alert("Please check your LionDocs configuration")

    return wrapper


def alert(message: str) -> None:
    config = Config()

    if config.alerts:
        sublime.message_dialog(message)
    else:
        echo("INFO", message)


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
            echo("INFO", "Selected file have a valid extension")

            # replace translated-content with content
            temp = str(target_file).replace(tcpath, cpath)
            config = Config()

            # replace en-us with target language
            lang = ipath(os.path.sep + config.lang_code)
            target_in_content = Path(temp.replace(lang, uspath))

            meta = None

            if target_in_content.is_file():
                echo("INFO", "File '{0}' exist".format(target_in_content))

                shaman = Shaman(target_in_content, config.content)  # here?
                meta = shaman.get_file_sha(returnas='meta')
            else:
                echo("INFO", "File '{}' doesn't exist. Switching extension".format(target_in_content))

                # try switching extension for find target file
                switch_ext = target_in_content.with_suffix(exts_dict[file_ext])
                target_in_content = switch_ext

                if target_in_content.is_file():
                    echo("INFO", "File '{0}' exist".format(target_in_content))

                    shaman = Shaman(target_in_content, config.content)
                    meta = shaman.get_file_sha(returnas='meta')
                else:
                    # ??? File doesn't exist in content? Update content repo
                    # raise Exception('File does not exist in content?')
                    echo("FATAL", "File '{}' doesn't exist, please sync your fork".format(target_in_content))
                    return

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
        config = Config()

        # replace en-us with target language
        lang = ipath(os.path.sep + config.lang_code)
        final_file_path = temp.replace(uspath, lang)

        # get final file dir tree
        dir_tree = ipath(final_file_path, parent=True)

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
                shaman = Shaman(file_to_transfer, config.content)
                meta = shaman.get_file_sha(returnas='meta')

                sep_index = [i.start() for i in re.finditer('---', original_content)][1]  # get separator index
                final_content = original_content[:sep_index] + meta + "\n" + original_content[sep_index:]
                final_file.write(final_content)

                alert("File with sourceCommit transfered successfully!")
