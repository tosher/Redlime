#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
from .rl_issue_field_change import RedlimeIssueFieldChangeCommand


class RedlimeChangeSubjectCommand(RedlimeIssueFieldChangeCommand):

    def change(self):
        self.view.window().show_input_panel("Subject:", self.issue.subject, self.on_done, None, None)

    def on_done(self, text):
        if text:
            self.issue.subject = text
            self.issue.save()
            self.view.window().status_message('Subject changed!')
            self.refresh()
