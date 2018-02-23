#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import rl_utils as utils
# from .rl_utils import Redlime


class RedlimeFetchQueryCommand(sublime_plugin.TextCommand):
    def run(self, edit, project_id, query_id, query_project_name):
        r = self.view.window().new_file()
        title = '%s (%s)' % (query_project_name[0], query_project_name[1])
        r.set_name(title)
        r.set_scratch(True)
        syntax_file = utils.rl_get_setting('syntax_file', 'Packages/Redlime/Redlime.tmLanguage')
        r.set_syntax_file(syntax_file)
        limit = utils.rl_get_setting('query_page_size', 40)
        page_number = 1
        query_params = {
            'project_id': project_id,
            'query_id': query_id,
            'limit': limit,
            'offset': 0,
            'page_number': page_number,
            'status_id': 'open'
        }
        content = utils.rl_show_issues(title=title, **query_params)
        r.settings().set('query_params', query_params)
        r.settings().set('title', title)
        r.settings().set('screen', 'redlime_query')

        r.settings().set("word_wrap", False)
        r.run_command('redlime_insert_text', {'position': 0, 'text': content})
        r.set_read_only(True)
