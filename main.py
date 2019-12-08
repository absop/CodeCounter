import re
import os
import time

import sublime
import sublime_plugin

from .lib import Loger
from .lib import counter
from .lib import strsize


singleline = "%20s│%15s│%12s│%12s"
tabulation = """
════════════════════╤═══════════════╤════════════╤════════════
{caption}
────────────────────┼───────────────┼────────────┼────────────
{content}
════════════════════╧═══════════════╧════════════╧════════════
"""
summary = """
────────────────────┼───────────────┼────────────┼────────────
{}"""
link_sheet = """
══════════╤════════╤══════════════════════════════════════════
      Size│   Lines│  Paths
──────────┼────────┼──────────────────────────────────────────
{}
══════════╧════════╧══════════════════════════════════════════
"""


class CodeCounterToggleLogCommand(sublime_plugin.WindowCommand):
    def run(self):
        Loger.debug = not Loger.debug


class SideBarFilesSizeCommand(sublime_plugin.WindowCommand):
    def is_visible(self, paths):
        return len(paths) == 1 and os.path.exists(paths[0])

    def run(self, paths):
        function = lambda:self.wait_on_path(paths[0])
        Loger.threading(function, "Counting...", "Succeed.")

    def wait_on_path(self, path):
        def strsize1(bytesize):
            s = strsize(bytesize)
            return s + "(%s Bytes)" % (bytesize)

        if os.path.isfile(path):
            content = (
                "PATH: {}\n"
                "Size: {}").format(path, strsize1(os.path.getsize(path)))
        else:
            info = self.get_path_info(path)
            content = (
                "ROOTDIR: {}\n"
                "TotalSize:\t{}\n"
                "Contains:\tFiles: {}, Folders: {}").format(
                path, strsize1(info[0]), info[1], info[2])

        panel = self.window.create_output_panel("Files Size")
        panel.assign_syntax("files-size.sublime-syntax")
        panel.run_command('append', {'characters': content})
        self.window.run_command(
                "show_panel", {"panel": "output.Files Size"})

    def get_path_info(self, path):
        def walk_dir(dir):
            for name in os.listdir(dir):
                path = os.path.join(dir, name)
                info[0] += os.path.getsize(path)
                if os.path.isfile(path):
                    info[1] += 1
                else:
                    info[2] += 1
                    walk_dir(path)
        info = [0, 0, 0]
        walk_dir(path)
        return info


class CodeCounterCountDirCommand(sublime_plugin.WindowCommand):
    def show_input_panel(self, caption, initial_text, on_done):
        v = self.window.show_input_panel(
            caption, initial_text, on_done, None, None)
        v.sel().clear()
        v.sel().add(sublime.Region(0, len(initial_text)))

    def accept_path(self, rootdir):
        def gen_regex(pattern):
            regex, needp = str(), False
            for c in pattern.strip(';'):
                if c in '$^?.+\\()[]':
                    regex += '\\' + c
                elif c == ';':
                    regex += '|'
                    needp = True
                elif c == '*':
                    regex += '.*'
                else:
                    regex += c
            if sublime.platform() == "windows":
                regex = regex.replace("/", "\\\\")

            return "(%s)" % regex if needp else regex

        def accept_regex(pattern):
            try:
                pattern = pattern and gen_regex(pattern)
                Loger.print("pattern = '%s'"% (pattern))
                regex = pattern and re.compile(pattern)
            except:
                Loger.error("Invalid pattern")
                return
            filter = lambda x: not regex.search(x) if regex else lambda x: True
            CodeCounterViewsManager.do_count(rootdir, filter)

        return accept_regex

    def run(self):
        self.show_input_panel("Path",
            self.window.active_view().file_name() or "untitled",
            lambda x: self.accept_path(x)(None))


class CodeCounterCountDirFilteredCommand(CodeCounterCountDirCommand):
    def run(self):
        self.show_input_panel("Path",
            self.window.active_view().file_name() or "untitled",
            lambda path: self.show_input_panel("Pattern", "",
                lambda pattern: self.accept_path(path)(pattern)))


class SideBarCodeCounterCommand(CodeCounterCountDirCommand):
    def is_visible(self, paths):
        return len(paths) == 1 and os.path.isdir(paths[0])

    def run(self, paths):
        self.accept_path(paths[0])(None)


class SideBarCodeCounterFilteredCommand(SideBarCodeCounterCommand):
    def run(self, paths):
        accept_regex = self.accept_path(paths[0])
        self.show_input_panel("Pattern", "", accept_regex)


class CodeCounterDetailLanguageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.settings().has("code_overview"):
            pt = self.view.sel()[0].a
            CodeCounterViewsManager.try_detail(self.view, pt)


class CodeCounterOpenFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.settings().has("code_detail"):
            pt = self.view.sel()[0].a
            CodeCounterViewsManager.try_open_file(self.view, pt)


class CodeCounterViewsManager(sublime_plugin.EventListener):
    underlined_views = {}
    language_extensions = {}
    language_fullnames = {}

    @classmethod
    def try_open_file(cls, view, pt):
        rootdir = view.settings().get("rootdir")
        relpath = view.substr(view.extract_scope(pt))
        abspath = os.path.join(rootdir, relpath)
        if os.path.isfile(abspath):
            Loger.print("open source file:", abspath)
            view.window().open_file(abspath, sublime.ENCODED_POSITION)
            return True
        return False

    @classmethod
    def try_detail(cls, view, pt):
        code_overview = view.settings().get("code_overview")
        lang = view.substr(view.extract_scope(pt))
        if lang in code_overview:
            rootdir = view.settings().get("rootdir")
            ctime = view.settings().get("time")
            code_detail = code_overview[lang]
            cls.detail(view, rootdir, ctime, lang, code_detail)
            return True
        return False

    @classmethod
    def do_count(cls, rootdir, filter):
        def store_path(_lang, _type, _path, relpath):
            """ data structure layout:
            {
                language-name:  [
                    0: files size,
                    1: files number,
                    2: lines number,
                    3: {
                        extension/fullname: [(relpath, nlines, fsize) ...]
                        ...
                    }
                ],
                ...
            }
            """
            try:
                nlines = counter.count(_path)
            except:
                nlines = 0
            try:
                fsize = os.path.getsize(_path)
            except:
                fsize = 0

            if _lang not in counting_tree:
                counting_tree[_lang] = [
                    0,
                    0,
                    0,
                    {}
                ]
            lang_storage = counting_tree[_lang]

            lang_storage[0] += fsize
            lang_storage[1] += 1
            lang_storage[2] += nlines
            if _type not in lang_storage[3]:
                lang_storage[3][_type] = []

            lang_storage[3][_type].append((relpath, nlines, fsize))

        def handle_file(file, path, relpath="."):
            if file in cls.language_fullnames:
                _lang = cls.language_fullnames[file]
                _type = file
            else:
                _type = os.path.splitext(file)[1].lstrip(".")
                if _type not in cls.language_extensions:
                    return
                _lang = cls.language_extensions[_type]
            store_path(_lang, _type, path, relpath)

        def walk_dir(dir):
            for file in sorted(os.listdir(dir)):
                path = os.path.join(dir, file)
                relpath = os.path.relpath(path, rootdir)
                if not (os.path.exists(path) and filter(relpath)):
                    continue
                if os.path.isdir(path):
                    walk_dir(path)
                else:
                    handle_file(file, path, relpath)


        counting_tree = {}
        window = sublime.active_window()
        ctime = time.strftime("%Y/%m/%d/%H:%M")

        def threading_counting():
            try:
                if os.path.isdir(rootdir):
                    walk_dir(rootdir)
                else:
                    handle_file(os.path.split(rootdir)[1], rootdir)
                cls.overview(window, rootdir, ctime, counting_tree)
            except Exception as e:
                Loger.error(str(e))

        if cls.language_extensions or cls.language_fullnames:
            Loger.threading(threading_counting,
                            "Counting...",
                            "Successful counting lines.")

    @classmethod
    def overview(cls, window, rootdir, ctime, overview_tree):
        total_files_size = 0
        total_files_number = 0
        total_lines_number = 0
        itmes = []
        for lang in sorted(overview_tree):
            tuple4 = overview_tree[lang]
            total_files_size += tuple4[0]
            total_files_number += tuple4[1]
            total_lines_number += tuple4[2]
            sstr = strsize(tuple4[0])
            itmes.append(singleline % (lang, sstr, tuple4[1], tuple4[2]))

        caption = singleline % ("Languages", "Size", "Files", "Lines")
        content = "\n".join(itmes)
        if len(itmes) > 1:
            content += summary.format(singleline % ("Total",
                strsize(total_files_size),
                total_files_number,
                total_lines_number))

        overview_text = "ROOTDIR: %s\nTime: %s\n\n\n" % (rootdir, ctime)
        overview_text += tabulation.format(caption=caption, content=content)

        view = window.new_file()
        view.assign_syntax("code-counter.sublime-syntax")
        view.set_name("CodeCounter - Overview")
        view.settings().set('word_wrap', False)
        view.settings().set('translate_tabs_to_spaces', True)
        view.settings().set("rootdir", rootdir)
        view.settings().set("time", ctime)
        view.settings().set("code_overview", overview_tree)
        view.run_command('append', {'characters': overview_text})
        view.set_scratch(True)
        view.set_read_only(True)
        cls.add_underline_for_paths(view)

    @classmethod
    def detail(cls, view, rootdir, ctime, lang, detail_tree):
        Loger.print("Detail language:", lang)
        fsize, fnumber, lnumber, types = detail_tree
        itmes, paths = [], []
        for _type in sorted(types):
            tuple3s = types[_type]
            files_size, lines_number = 0, 0
            for relpath, nl, fs in tuple3s:
                files_size += fs
                lines_number += nl
                fs = strsize(fs)
                paths.append("%10s│%8d│  %s" % (fs, nl, relpath))
            itmes.append(singleline % (_type[:20],
                strsize(files_size), len(tuple3s), lines_number))

        caption = singleline %("Types", "Size", "Files", "Lines")
        content = "\n".join(itmes)
        if len(itmes) > 1:
            content += summary.format(singleline %("Total",
                strsize(fsize), fnumber, lnumber))

        detail_text = "ROOTDIR: %s\nTime: %s\n\n\n" % (rootdir, ctime)
        detail_text += tabulation.format(caption=caption, content=content)
        detail_text += "\n\n\n" + link_sheet.format("\n".join(paths))

        v = view.window().new_file()
        v.assign_syntax("code-counter.sublime-syntax")
        v.set_name("CodeCounter - %s" % lang)
        v.settings().set('word_wrap', False)
        v.settings().set('translate_tabs_to_spaces', True)
        v.settings().set("rootdir", rootdir)
        v.settings().set("code_detail", lang)
        v.run_command('append', {'characters': detail_text})
        v.set_scratch(True)
        v.set_read_only(True)
        cls.add_underline_for_paths(v)

    @classmethod
    def add_underline_for_paths(cls, view):
        regions = view.find_by_selector("entity.name.filename")
        view.add_regions("code-counter", regions,
            scope="entity.name.filename",
            flags=sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|
                sublime.DRAW_SOLID_UNDERLINE|sublime.HIDE_ON_MINIMAP)
        cls.underlined_views[view.view_id] = True

    @classmethod
    def try_add_underlines(cls, view):
        if view.view_id in cls.underlined_views:
            return
        if (view.settings().has("code_detail") or
            view.settings().has("code_overview")):
            cls.add_underline_for_paths(view)

    def on_activated(self, view):
        CodeCounterViewsManager.try_add_underlines(view)

    def on_load(self, view):
        CodeCounterViewsManager.try_add_underlines(view)

    def on_text_command(self, view, name, args):
        if name == "drag_select" and args.get("by", "") == "words":
            event = args["event"]
            pt = view.window_to_text((event["x"], event["y"]))
            if view.settings().has("code_detail"):
                if CodeCounterViewsManager.try_open_file(view, pt):
                    return (name, args)
            elif view.settings().has("code_overview"):
                if CodeCounterViewsManager.try_detail(view, pt):
                    return (name, args)


def configure_code_counter(settings):
    extensions = settings.get("extensions", {})
    fullnames = settings.get("fullnames", {})

    if not (extensions or fullnames):
        emsg = "No languages are added, please check your settings file."
        Loger.error(emsg)
        return

    language_extensions = {}
    for lang in extensions:
        for ext in extensions[lang]:
            if ext in language_extensions:
                old_lang = extensions[ext]
                fmt = "Extension '%s' is owned by multi-languages: %s %s"
                Loger.error(fmt % (ext, old_lang, lang))
                return None
            language_extensions[ext] = lang

    language_fullnames = {}
    for lang in fullnames:
        for fname in fullnames[lang]:
            if fname in language_fullnames:
                fmt = "Fullname '%s' is owned by multi-languages: %s %s"
                Loger.error(fmt % (fname, fullnames[fname], lang))
                return None
            language_fullnames[fname] = lang

    CodeCounterViewsManager.language_extensions = language_extensions
    CodeCounterViewsManager.language_fullnames = language_fullnames

    counter.set_encoding(settings.get("encoding", 'utf-8'))


settings_error = """
There are some error in the process of loading settings.
Please restart Sublime Text to make sure that settings are loaded properly.
"""

def plugin_loaded():
    settings = sublime.load_settings("CodeCounter.sublime-settings")

    def configure():
        configure_code_counter(settings)

    try:
        settings.add_on_change("encoding", configure)
        configure()
    except:
        sublime.error_message(settings_error)

    counter.load_binary()


def plugin_unloaded():
    counter.unload_binary()
