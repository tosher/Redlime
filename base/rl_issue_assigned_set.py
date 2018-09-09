#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime


class RedlimeSetAssignedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(index):
            if index >= 0:
                assigned_to_id = users[index].id
                issue.assigned_to_id = assigned_to_id
                issue.save()

                self.view.window().status_message('Issue #%r is assigned to %s!' % (issue.id, users_menu[index]))
                self.view.run_command('redlime_fetcher', {'issue_id': issue.id})

        redmine = Redlime.connect()
        users = []
        users_menu = []
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            issue = redmine.issue.get(issue_id)
            groups = utils.rl_get_setting('assigned_to_group_id_filter', [])  # user group filter
            if groups:
                for group_id in groups:
                    for user in redmine.user.filter(group_id=group_id):
                        if user.id not in [user.id for user in users]:
                            users.append(user)
            else:
                project_id = issue.project.id
                users = [redmine.user.get(user.user.id) for user in redmine.project_membership.filter(project_id=project_id) if hasattr(user, 'user')]

            if users:
                for user in users:
                    users_menu.append('%s %s' % (user.firstname, user.lastname))
                sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(users_menu, on_done), 1)

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
