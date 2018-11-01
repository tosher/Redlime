#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
from .rl_issue_field_change import RedlimeIssueFieldChangeCommand


class RedlimePriorityIssueCommand(RedlimeIssueFieldChangeCommand):

    def change(self):
        enumerations = self.redmine.enumeration.filter(resource='issue_priorities')
        enums = []
        self.enums_ids = []
        for enum in enumerations:
            enums.append(enum.name)
            self.enums_ids.append(enum.id)

        sublime.set_timeout(lambda: self.view.window().show_quick_panel(enums, self.on_done), 1)

    def on_done(self, idx):
        if idx >= 0:
            self.issue.priority_id = self.enums_ids[idx]
            self.issue.save()
            self.view.window().status_message('Priority changed!')
            self.refresh()
