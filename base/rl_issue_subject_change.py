#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime


class RedlimeChangeSubjectCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(text):
            if text:
                if issue_id != 0:
                    issue.subject = text
                    issue.save()
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        redmine = Redlime.connect()
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            issue = redmine.issue.get(issue_id)
            self.view.window().show_input_panel("Subject:", issue.subject, on_done, None, None)

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
