#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils
from .utils import Redlime


class RedlimeAssignFilterCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.users = []
        self.users_menu = ['*All users']
        redmine = Redlime.connect()
        groups = utils.get_setting('assigned_to_group_id_filter', [])  # user group filter
        if groups:
            for group_id in groups:
                for user in redmine.user.filter(group_id=group_id):
                    if user.id not in [user.id for user in self.users]:
                        self.users.append(user)
        else:
            query_params = self.view.settings().get('query_params', {})
            project_id = query_params.get('project_id')
            # self.users = [redmine.user.get(user.user.id) for user in redmine.project_membership.filter(project_id=project_id) if hasattr(user, 'user')]
            self.users = [user.user for user in redmine.project_membership.filter(project_id=project_id) if hasattr(user, 'user')]

        if self.users:
            for user in self.users:
                # self.users_menu.append('%s %s' % (user.firstname, user.lastname))
                self.users_menu.append(user.name)
            self.view.window().show_quick_panel(self.users_menu, self.on_done)

    def on_done(self, idx):
        query_params = self.view.settings().get('query_params', {})
        limit = utils.get_setting('query_page_size', 40)
        query_params['limit'] = limit
        query_params['offset'] = 0
        query_params['page_number'] = 1
        if idx == 0:
            query_params.pop('assigned_to_id', None)
            self.view.settings().set('query_params', query_params)
        elif idx > 0:
            query_params['assigned_to_id'] = self.users[idx - 1].id
            self.view.settings().set('query_params', query_params)
        self.view.run_command('redlime_issues_refresh')

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_list')
        ]
        if screen in valid_screens:
            return True
        return False
