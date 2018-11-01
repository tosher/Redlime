#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils


class RedlimeOpenSubissueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        issue_id = None
        try:
            issue_id = self.view.substr(self.view.sel()[0]).split(':')[0]
            int(issue_id)
        except Exception:
            pass

        if issue_id:
            self.view.run_command('redlime_issue', {'issue_id': issue_id})

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
