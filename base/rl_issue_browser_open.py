#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import webbrowser
# import sublime
import sublime_plugin
from . import rl_utils as utils


class RedlimeGoRedmineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            url = '%s/issues/%s' % (utils.rl_get_setting('redmine_url').rstrip('/'), issue_id)
            webbrowser.open(url)

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
