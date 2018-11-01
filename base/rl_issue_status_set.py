#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from .rl_issue_field_change import RedlimeIssueFieldChangeCommand


class RedlimeSetStatusCommand(RedlimeIssueFieldChangeCommand):

    def change(self):
        statuses = self.redmine.issue_status.all()
        self.statuses_names = []
        self.statuses_ids = []
        for status in statuses:
            self.statuses_names.append(status.name)
            self.statuses_ids.append(status.id)

        self.view.window().show_quick_panel(self.statuses_names, self.on_done)

    def on_done(self, idx):
        if idx > -1:
            self.issue.status_id = self.statuses_ids[idx]
            self.issue.save()
            self.view.window().status_message('Issue #%r now is %s' % (self.issue.id, self.statuses_names[idx]))
            self.refresh()
