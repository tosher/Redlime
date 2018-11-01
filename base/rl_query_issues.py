#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils
# from .utils import Redlime


class RedlimeFetchQueryCommand(sublime_plugin.TextCommand):
    def run(self, edit, project_id, query_id, query_project_name):
        r = self.view.window().new_file()
        title = '%s (%s)' % (query_project_name[0], query_project_name[1])
        r.set_name(title)
        r.set_scratch(True)
        syntax_file = utils.get_setting('syntax_file', 'Packages/Redlime/Redlime.tmLanguage')
        r.set_syntax_file(syntax_file)
        limit = utils.get_setting('query_page_size', 40)
        page_number = 1
        query_params = {
            'project_id': project_id,
            'query_id': query_id,
            'limit': limit,
            'offset': 0,
            'page_number': page_number,
            'status_id': 'open'
        }
        issues = utils.rl_filter_issues(**query_params)
        content = utils.rl_show_issues(title=title, issues=issues, **query_params)
        r.settings().set('query_params', query_params)
        r.settings().set('title', title)
        r.settings().set('screen', 'redlime_query')

        r.settings().set("word_wrap", False)
        r.run_command('redlime_insert_text', {'position': 0, 'text': content})
        r.set_read_only(True)
