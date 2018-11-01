#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
from . import utils
from .rl_issue_field_change import RedlimeIssueFieldChangeCommand


class RedlimeSetAssignedCommand(RedlimeIssueFieldChangeCommand):

    def change(self):
        self.users = []
        self.users_menu = []

        groups = utils.get_setting('assigned_to_group_id_filter', [])  # user group filter
        if groups:
            for group_id in groups:
                for user in self.redmine.user.filter(group_id=group_id):
                    if user.id not in [user.id for user in self.users]:
                        self.users.append(user)
        else:
            project_id = self.issue.project.id
            self.users = [self.redmine.user.get(user.user.id) for user in self.redmine.project_membership.filter(project_id=project_id) if hasattr(user, 'user')]

        if self.users:
            for user in self.users:
                self.users_menu.append('%s %s' % (user.firstname, user.lastname))
            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(self.users_menu, self.on_done), 1)

    def on_done(self, index):
        if index >= 0:
            assigned_to_id = self.users[index].id
            self.issue.assigned_to_id = assigned_to_id
            self.issue.save()
            self.view.window().status_message('Issue #%r is assigned to %s!' % (self.issue.id, self.users_menu[index]))
            self.refresh()
