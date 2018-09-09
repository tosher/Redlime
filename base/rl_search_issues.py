#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import rl_utils as utils
# from .rl_utils import Redlime


class RedlimeSearchIssuesCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.view.window().show_input_panel("Search:", '', self.on_done, None, None)

    def on_done(self, text):
        if not text:
            return

        search_params = {
            'titles_only': False,
            'open_issues': False,
            'attachments': True,
            'scope': 'my_projects'
        }

        issues = utils.rl_search_issues(text, **search_params)
        title = 'Issues search: %s' % text
        text = utils.rl_show_issues(title=title, issues=issues)
        r = self.view.window().new_file()
        r.set_name(title)
        syntax_file = utils.rl_get_setting('syntax_file', 'Packages/Redlime/Redlime.tmLanguage')
        r.set_syntax_file(syntax_file)
        r.settings().set('query_params', {})
        r.settings().set('title', title)
        r.settings().set('screen', 'redlime_query')
        r.settings().set("word_wrap", False)
        r.run_command('redlime_insert_text', {'position': 0, 'text': text})
        r.set_scratch(True)
        r.set_read_only(True)
