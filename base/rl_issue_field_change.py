#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime_plugin
from . import utils
from .utils import Redlime


class RedlimeIssueFieldChangeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.screen = self.view.settings().get('screen')
        issue_id = self.get_issue_id()
        if issue_id:
            self.setup(issue_id)
            self.change()

    def change(self):
        pass

    def refresh(self):
        if self.screen == 'redlime_issue':
            self.view.run_command('redlime_fetcher', {'issue_id': self.issue.id})
        elif self.screen == 'redlime_query':
            self.view.run_command('redlime_issues_refresh')

    def get_issue_id(self):
        if self.screen == 'redlime_issue':
            issue_id = self.view.settings().get('issue_id', None)
        elif self.screen == 'redlime_query':
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                issue_id = line.split(utils.TABLE_SEP)[1].strip()
                int(issue_id)  # check is number
            except Exception:
                pass
        return issue_id

    def setup(self, issue_id):
        self.redmine = Redlime.connect()
        self.issue = self.redmine.issue.get(issue_id)

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_view'),
            utils.object_commands.get('issue', {}).get('screen_list')
        ]
        if screen in valid_screens:
            return True
        return False
