#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import rl_utils as utils


class RedlimeRefreshIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            self.view.run_command('redlime_fetcher', {'issue_id': issue_id})
            self.view.window().status_message('Issue Refreshed!')

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
