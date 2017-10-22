#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from .base import *  # noqa


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
