#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
# import sublime_plugin
from . import utils
# from .utils import Redlime
from .rl_issue_field_change import RedlimeIssueFieldChangeCommand


class RedlimeChangeProjectCommand(RedlimeIssueFieldChangeCommand):

    def change(self):
        projects_filter = utils.get_setting('projects_filter', [])
        if projects_filter:
            self.projects = [self.redmine.project.get(pid) for pid in projects_filter]
        else:
            self.projects = self.redmine.project.all()
        projects_names = [prj.name for prj in self.projects]

        self.view.window().show_quick_panel(projects_names, self.on_done)

    def on_done(self, idx):
        if idx >= 0:
            self.issue.project_id = self.projects[idx].id
            self.issue.save()
            self.view.window().status_message('Issue #%r is moved to %s' % (self.issue.id, self.projects[idx].name))
            self.refresh()

# class RedlimeChangeProjectCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         def on_done(i):
#             if i >= 0:
#                 if issue_id != 0:
#                     issue = redmine.issue.get(issue_id)
#                     issue.project_id = projects[i].id
#                     issue.save()
#                     self.view.window().status_message('Issue #%r is moved to %s' % (issue.id, projects[i].name))
#                     self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

#         redmine = Redlime.connect()
#         issue_id = self.view.settings().get('issue_id', None)
#         if issue_id:
#             projects_filter = utils.get_setting('projects_filter', [])
#             if projects_filter:
#                 projects = [redmine.project.get(pid) for pid in projects_filter]
#             else:
#                 projects = redmine.project.all()
#             projects_names = [prj.name for prj in projects]

#             self.view.window().show_quick_panel(projects_names, on_done)

#     def is_visible(self, *args):
#         screen = self.view.settings().get('screen')
#         if not screen:
#             return False
#         valid_screens = [
#             utils.object_commands.get('issue', {}).get('screen_view')
#         ]
#         if screen in valid_screens:
#             return True
#         return False
