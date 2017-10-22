#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime


class RedlimeChangeProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(i):
            if i >= 0:
                if issue_id != 0:
                    issue = redmine.issue.get(issue_id)
                    issue.project_id = projects[i].id
                    issue.save()
                    sublime.status_message('Issue #%r is moved to %s' % (issue.id, projects[i].name))
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        redmine = Redlime.connect()
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            projects_filter = utils.rl_get_setting('projects_filter', [])
            if projects_filter:
                projects = [redmine.project.get(pid) for pid in projects_filter]
            else:
                projects = redmine.project.all()
            projects_names = [prj.name for prj in projects]

            self.view.window().show_quick_panel(projects_names, on_done)

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
