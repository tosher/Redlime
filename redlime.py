#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from .base import *  # noqa
from .base.shortcuts_menu import ShortcutsMenu
from .base import rl_utils as utils


class RedlimeViewEvents(sublime_plugin.ViewEventListener):

    def on_query_context(self, key, operator, operand, match_all):
        if key == 'rl_screen':
            if operator == sublime.OP_EQUAL:
                if isinstance(operand, list):
                    return self.view.settings().get('screen', None) in operand
                else:

                    # print(key, operand, type(operand), operand == view.settings().get('screen', None))
                    return operand == self.view.settings().get('screen', None)
            if operator == sublime.OP_NOT_EQUAL:
                if isinstance(operand, list):
                    return self.view.settings().get('screen', None) not in operand
                else:
                    return operand != self.view.settings().get('screen', None)

    def on_activated_async(self):
        screen = self.view.settings().get('screen')
        if not screen or not screen.startswith('redlime'):
            return
        if screen == 'redlime_query':
            is_query = bool(self.view.settings().get('query_params').get('query_id', None))
            shortcuts = utils.shortcuts_issue_list_query if is_query else utils.shortcuts_issue_list_project
            cols = utils.cols_issue_list_query if is_query else utils.cols_issue_list_project
            ShortcutsMenu(
                self.view,
                shortcuts=shortcuts,
                cols=cols
            )
        elif screen == 'redlime_issue':
            ShortcutsMenu(
                self.view,
                shortcuts=utils.shortcuts_issue_edit,
                cols=utils.cols_issue_edit
            )


class RedlimeEvents(sublime_plugin.EventListener):

    def is_screen_read_only(self, screen, view):
        if screen == 'redlime_query':
            return True
        elif screen == 'redlime_issue' and view.settings().get('redlime_issue_unselectable', True):
            return True
        return False

    def on_selection_modified(self, view):
        screen = view.settings().get('screen')
        if not screen:
            return

        if view.is_read_only() and self.is_screen_read_only(screen, view):
            view.sel().add(view.line(view.sel()[0].end()))


