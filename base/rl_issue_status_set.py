#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime


class RedlimeSetStatusCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(i):
            if i > -1:
                if issue_id != 0:
                    issue = redmine.issue.get(issue_id)
                    issue.status_id = statuses_ids[i]
                    issue.save()
                    sublime.status_message('Issue #%r now is %s' % (issue.id, statuses_names[i]))
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        redmine = Redlime.connect()
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            statuses = redmine.issue_status.all()
            statuses_names = []
            statuses_ids = []
            for status in statuses:
                statuses_names.append(status.name)
                statuses_ids.append(status.id)

            self.view.window().show_quick_panel(statuses_names, on_done)

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False
