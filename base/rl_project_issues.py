#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils
from .utils import Redlime


class RedlimeProjectIssuesCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        redmine = Redlime.connect()
        projects_filter = utils.get_setting('projects_filter', [])
        if projects_filter:
            projects = [redmine.project.get(pid) for pid in projects_filter]
        else:
            projects = redmine.project.all()

        self.prj_names = []
        self.prj_ids = []
        for prj in projects:
            self.prj_names.append(prj.name)
            self.prj_ids.append(prj.id)
        self.view.window().show_quick_panel(self.prj_names, self.on_done)

    def on_done(self, idx):
        if idx >= 0:
            title = 'Issues: %s' % self.prj_names[idx]
            limit = utils.get_setting('query_page_size', 40)
            query_params = {
                'project_id': self.prj_ids[idx],
                'limit': limit,
                'offset': 0,
                'page_number': 1,
                'status_id': 'open'
            }
            # text = utils.rl_show_cases(**query_params)
            issues = utils.rl_filter_issues(**query_params)
            text = utils.rl_show_issues(title=title, issues=issues, **query_params)
            r = self.view.window().new_file()
            r.set_name(title)
            syntax_file = utils.get_setting('syntax_file', 'Packages/Redlime/Redlime.tmLanguage')
            r.set_syntax_file(syntax_file)
            r.settings().set('query_params', query_params)
            r.settings().set('title', title)
            r.settings().set('screen', 'redlime_query')
            r.settings().set("word_wrap", False)
            r.run_command('redlime_insert_text', {'position': 0, 'text': text})
            r.set_scratch(True)
            r.set_read_only(True)
