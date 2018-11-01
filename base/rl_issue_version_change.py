#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
from .rl_issue_field_change import RedlimeIssueFieldChangeCommand


class RedlimeVersionIssueCommand(RedlimeIssueFieldChangeCommand):

    def change(self):
        project_versions = []
        self.project_version_ids = []
        for ver in self.issue.project.versions:
            project_versions.append(ver.name)
            self.project_version_ids.append(ver.id)

        sublime.set_timeout(lambda: self.view.window().show_quick_panel(project_versions, self.on_done), 1)

    def on_done(self, idx):
            if idx >= 0:
                self.issue.fixed_version_id = self.project_version_ids[idx]
                self.issue.save()
                self.view.window().status_message('Version changed!')
                self.refresh()
