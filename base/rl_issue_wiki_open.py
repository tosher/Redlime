#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import webbrowser
# import sublime
import sublime_plugin
from . import utils
from .utils import Redlime


class RedlimeOpenWikiCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        field_prop = utils.get_setting('external_wiki_field', None)
        if field_prop:
            wiki_url = ''
            issue_id = self.view.settings().get('issue_id', None)
            if issue_id:
                redmine = Redlime.connect()
                issue = redmine.issue.get(issue_id)
                if hasattr(issue, 'custom_fields'):
                    for field in issue.custom_fields:
                        if field['name'] == field_prop:
                            wiki_url = field['value']
                            break

                    if wiki_url:
                        webbrowser.open(wiki_url)

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
