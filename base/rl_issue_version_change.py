#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime


class RedlimeVersionIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(idx):
            if idx >= 0:
                issue.fixed_version_id = project_version_ids[idx]
                issue.save()
                self.view.window().status_message('Version changed!')
                self.view.run_command('redlime_fetcher', {'issue_id': issue.id})

        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            redmine = Redlime.connect()
            issue = redmine.issue.get(issue_id)
            project_versions = []
            project_version_ids = []
            for ver in issue.project.versions:
                project_versions.append(ver.name)
                project_version_ids.append(ver.id)

            sublime.set_timeout(lambda: self.view.window().show_quick_panel(project_versions, on_done), 1)

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
