#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import rl_utils as utils
# from .rl_utils import Redlime


class RedlimeIssuesRefreshCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        query_params = self.view.settings().get('query_params')
        limit = utils.rl_get_setting('query_page_size', 40)
        query_params['limit'] = limit
        if query_params:
            text = utils.rl_show_cases(**query_params)
            self.view.set_read_only(False)
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            self.view.run_command('redlime_insert_text', {'position': 0, 'text': text})
            self.view.set_read_only(True)

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_list')
        ]
        if screen in valid_screens:
            return True
        return False

