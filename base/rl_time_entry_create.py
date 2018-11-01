#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import datetime
import sublime
import sublime_plugin
from . import utils
from .utils import Redlime


class RedlimeTimeEntryCreateCommand(sublime_plugin.TextCommand):

    timeentry_data = {}

    def run(self, edit):
        self.redmine = Redlime.connect()
        # issue_id = self.view.settings().get('issue_id', None)
        self.screen = self.view.settings().get('screen')
        issue_id = self.get_issue_id()
        if issue_id is None:
            projects_filter = utils.get_setting('projects_filter', [])
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
        else:
            self.on_issue_done(issue_id)

    def get_issue_id(self):
        issue_id = None
        if self.screen == 'redlime_issue':
            issue_id = self.view.settings().get('issue_id', None)
        elif self.screen == 'redlime_query':
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                issue_id = line.split(utils.TABLE_SEP)[1].strip()
                int(issue_id)  # check is number
            except Exception:
                pass
        return issue_id

    def on_project_done(self, index):
        if index < 0:
            return

        self.timeentry_data['project_id'] = self.prj_ids[index]
        self.view.window().show_input_panel("Issue id:", '', self.on_issue_done, None, None)

    def on_issue_done(self, text):
        if text:
            self.timeentry_data['issue_id'] = int(text)

        activities = self.redmine.enumeration.filter(resource='time_entry_activities')
        if activities:
            self.acts = []
            self.acts_ids = []
            for enum in activities:
                self.acts.append(enum.name)
                self.acts_ids.append(enum.id)

            sublime.set_timeout(lambda: self.view.window().show_quick_panel(self.acts, self.on_activity_done), 1)
        else:
            self.on_activity_done(-1)

    def on_activity_done(self, index):
        if index >= 0:
            # not required and needs redmine >= 3.4.0
            self.timeentry_data['activity_id'] = self.acts_ids[index]
            self.timeentry_data['activity_name'] = self.acts[index]

        self.view.window().show_input_panel("Date:", datetime.datetime.now().strftime('%Y-%m-%d'), self.on_date_done, None, None)

    def on_date_done(self, text):
        if not text:
            return
        self.timeentry_data['spent_on'] = text

        self.view.window().show_input_panel("Hours:", '1.0', self.on_hours_done, None, None)

    def on_hours_done(self, text):
        if not text:
            return
        self.timeentry_data['hours'] = float(text)

        self.view.window().show_input_panel("Comment:", '', self.on_comment_done, None, None)

    def on_comment_done(self, text):
        if not text:
            return

        time_entry = self.redmine.time_entry.new()
        if self.timeentry_data.get('issue_id', None):
            time_entry.issue_id = self.timeentry_data['issue_id']
        elif self.timeentry_data.get('project_id', None):
            time_entry.project_id = self.timeentry_data['project_id']
        else:
            raise Exception('Issue or project required to create time entry.')
        if self.timeentry_data.get('activity_id', None):
            time_entry.activity_id = self.timeentry_data.get('activity_id', None)
        time_entry.comments = text
        time_entry.spent_on = self.timeentry_data['spent_on']
        time_entry.hours = self.timeentry_data['hours']
        time_entry.save()
        if time_entry.id:
            sublime.message_dialog('Time entry %s ("%s: %s") created successfully.' % (time_entry.id, self.timeentry_data['activity_name'], time_entry.comments))
            if self.timeentry_data['issue_id']:
                self.view.run_command('redlime_issue', {'issue_id': self.timeentry_data['issue_id']})
        else:
            sublime.message_dialog('Error! Time entry creation failed..')
