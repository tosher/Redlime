#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import utils
# from .utils import Redlime


class RedlimeIssuesPageCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction):
        query_params = self.view.settings().get('query_params')
        title = self.view.settings().get('title')
        limit = utils.get_setting('query_page_size', 40)
        offset = query_params.get('offset', 0)
        page_number = query_params.get('page_number', 1)
        if direction:
            offset_new = offset + limit
            page_number = page_number + 1
        else:
            offset_new = offset - limit
            offset_new = offset_new if offset_new >= 0 else 0
            page_number = page_number - 1
            page_number = page_number if page_number >= 1 else 1
        query_params['page_number'] = page_number
        query_params['offset'] = offset_new
        query_params['limit'] = limit
        self.view.settings().set('query_params', query_params)

        if query_params:
            issues = utils.rl_filter_issues(**query_params)
            text = utils.rl_show_issues(title=title, issues=issues, **query_params)
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
