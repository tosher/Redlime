#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import webbrowser
# import sublime
import sublime_plugin
from . import utils


class RedlimeOpenLinkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        url = self.view.substr(self.view.sel()[0]).split('(')[1].rstrip(')')
        if url:
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
