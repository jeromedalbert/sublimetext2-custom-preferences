import sublime, sublime_plugin, re


class RevealInSideBarAndFocus(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().run_command("reveal_in_side_bar")
        self.view.window().run_command("focus_side_bar")


class CloseOtherTabs(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()
        group_index, view_index = window.get_view_index(self.view)
        window.run_command("close_others_by_index", {"group": group_index, "index": view_index})


class NewRubyFile(sublime_plugin.TextCommand):
    def run(self, edit):
        f = self.view.window().new_file()
        f.set_syntax_file('Packages/Ruby/Ruby.tmLanguage')


class CustomCloseTab(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window

        if window.active_view() is None:
            if window.views():
                window.run_command("focus_side_bar")
            else:
                window.run_command("close_window")
            return

        group, index = window.get_view_index(window.active_view())
        window.run_command("close")

        views = window.views_in_group(group)
        if views:
            new_index = 0 if index == 0 else index - 1
            window.focus_view(views[new_index])
        else:
            window.run_command("focus_side_bar")


class SaveAndClose(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("save")
        self.window.run_command("close")


class FocusFindTab(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        find_tab = next((v for v in window.views() if v.name() == "Find Results"), None)
        if find_tab:
            window.focus_view(find_tab)


class ClearFindTab(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        find_tab = next((v for v in window.views() if v.name() == "Find Results"), None)
        if find_tab:
            edit = find_tab.begin_edit()
            find_tab.replace(edit, sublime.Region(0, find_tab.size()), '')
            find_tab.end_edit(edit)


class CustomFindInFiles(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("clear_find_tab")
        self.window.run_command("show_panel", {"panel": "find_in_files"})


class DisplayEncoding(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.message_dialog(self.view.encoding())


class CustomTrimTrailingWhiteSpaceAndEnsureNewLine(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        self.cursor = view.sel()[0]
        self.line_number = view.rowcol(self.cursor.end())[0]
        self.line_str = view.substr(view.line(self.cursor))
        self.indentation_added = False
        self.new_line_added = False
        self.trim_trailing_white_space(view)
        self.ensure_new_line_at_eof(view)

    def trim_trailing_white_space(self, view):
        if view.settings().get("trim_trailing_white_space_on_save") == True:
            trailing_white_space = view.find_all("[\t ]+$")
            trailing_white_space.reverse()
            edit = view.begin_edit()
            for r in trailing_white_space:
                view.erase(edit, r)
            view.end_edit(edit)
            if re.search(r'^\s*(\t|  )+$', self.line_str):
                view.run_command("reindent")
                self.indentation_added = True

    def ensure_new_line_at_eof(self, view):
        if view.settings().get("ensure_newline_at_eof_on_save") == True:
            if view.size() > 0 and (view.substr(view.size() - 1) != '\n'):
                if self.indentation_added == False or self.cursor.end() != view.size():
                    edit = view.begin_edit()
                    view.insert(edit, view.size(), "\n")
                    view.end_edit(edit)
                    self.new_line_added = True

    def on_post_save(self, view):
        if self.new_line_added == True:
            line = self.get_updated_line(view)
            view.sel().clear()
            view.sel().add(line.end())

    def get_updated_line(self, view):
        return view.line(view.text_point(self.line_number, 0))
