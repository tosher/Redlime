#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import datetime
import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime


class RedlimeIssueCreateCommand(sublime_plugin.TextCommand):

    ESTIMATED_HOURS_DEFAULT = 48
    issue_data = {}

    def run(self, edit):
        self.redmine = Redlime.connect()
        projects_filter = utils.rl_get_setting('projects_filter', [])
        if projects_filter:
            projects = [self.redmine.project.get(pid) for pid in projects_filter]
        else:
            projects = self.redmine.project.all()

        prj_names = []
        self.prj_ids = []
        for prj in projects:
            prj_names.append(prj.name)
            self.prj_ids.append(prj.id)
        self.view.window().show_quick_panel(prj_names, self.on_project_done)

    def on_project_done(self, index):
        if index < 0:
            return

        # self.project_id = self.prj_ids[index]
        self.issue_data['project_id'] = self.prj_ids[index]

        self.users = []
        groups = utils.rl_get_setting('assigned_to_group_id_filter', [])  # user group filter
        if groups:
            for group_id in groups:
                for user in self.redmine.user.filter(group_id=group_id):
                    if user.id not in [user.id for user in self.users]:
                        self.users.append(user)
        else:
            self.users = [self.redmine.user.get(user.user.id) for user in self.redmine.project_membership.filter(project_id=self.issue_data['project_id']) if hasattr(user, 'user')]

        users_menu = []
        for user in self.users:
            users_menu.append('%s %s' % (user.firstname, user.lastname))

        sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(users_menu, self.on_user_done), 1)

    def on_user_done(self, index):
        if index < 0:
            return
        # self.assigned_to_id = self.users[index].id
        self.issue_data['assigned_to_id'] = self.users[index].id

        trackers = self.redmine.tracker.all()
        trackers_names = []
        self.trackers_ids = []
        for tracker in trackers:
            trackers_names.append(tracker.name)
            self.trackers_ids.append(tracker.id)

        sublime.set_timeout(lambda: self.view.window().show_quick_panel(trackers_names, self.on_tracker_done), 1)

    def on_tracker_done(self, index):
        if index < 0:
            return
        # self.tracker_id = self.trackers_ids[index]
        self.issue_data['tracker_id'] = self.trackers_ids[index]

        self.view.window().show_input_panel("Subject:", '', self.on_subject_done, None, None)

    def on_subject_done(self, text):
        if not text:
            return

        issue = self.redmine.issue.new()
        issue.project_id = self.issue_data['project_id']
        issue.subject = text
        issue.tracker_id = self.issue_data['tracker_id']
        issue.description = ''
        issue.status_id = 1  # new
        issue.priority_id = 1  # low as default
        issue.assigned_to_id = self.issue_data['assigned_to_id']
        dt_start = datetime.datetime.now()  # Текущая дата и время
        estimated_hours = utils.rl_get_setting('issue_default_estimated_hours', self.ESTIMATED_HOURS_DEFAULT)
        dt_due = dt_start + datetime.timedelta(hours=estimated_hours)
        issue.start_date = dt_start.strftime('%Y-%m-%d')
        issue.due_date = dt_due.strftime('%Y-%m-%d')
        issue.estimated_hours = estimated_hours
        issue.done_ratio = 0
        issue.fixed_version_id = None
        issue.save()
        if issue.id:
            sublime.message_dialog('Issue %s ("%s") created successfully.' % (issue.id, issue.subject))
            self.view.run_command('redlime_issue', {'issue_id': issue.id})
        else:
            sublime.message_dialog('Error! Redmine issue creation failed..')
