#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime


class RedlimeDoneRatioIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(idx):
            if idx >= 0:
                issue.done_ratio = int(enums[idx])
                issue.save()
                sublime.status_message('Done ratio changed!')
                self.view.run_command('redlime_fetcher', {'issue_id': issue.id})

        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            redmine = Redlime.connect()
            issue = redmine.issue.get(issue_id)
            # https://github.com/redmine/redmine/blob/3.4-stable/app/views/issues/_attributes.html.erb#L72
            enums = [str(10 * x) for x in range(0, 11)]

            sublime.set_timeout(lambda: self.view.window().show_quick_panel(enums, on_done), 1)

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
