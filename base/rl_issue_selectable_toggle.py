#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import rl_utils as utils


class RedlimeToggleSelectableCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        is_unselectable = self.view.settings().get('redlime_issue_unselectable', True)
        if is_unselectable:
            self.view.settings().set('redlime_issue_unselectable', False)
        else:
            self.view.settings().set('redlime_issue_unselectable', True)

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
