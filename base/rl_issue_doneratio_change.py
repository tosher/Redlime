#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
from .rl_issue_field_change import RedlimeIssueFieldChangeCommand


class RedlimeDoneRatioIssueCommand(RedlimeIssueFieldChangeCommand):

    def change(self):
        # https://github.com/redmine/redmine/blob/3.4-stable/app/views/issues/_attributes.html.erb#L72
        self.enums = [str(10 * x) for x in range(0, 11)]

        sublime.set_timeout(lambda: self.view.window().show_quick_panel(self.enums, self.on_done), 1)

    def on_done(self, idx):
        if idx >= 0:
            self.issue.done_ratio = int(self.enums[idx])
            self.issue.save()
            self.view.window().status_message('Done ratio changed!')
            self.refresh()
