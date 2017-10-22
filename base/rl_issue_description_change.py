#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime
from .rl_editbox import RlEditbox


class RedlimeChangeDescriptionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        on_done = 'redlime_change_description_done'
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            redmine = Redlime.connect()
            issue = redmine.issue.get(issue_id)
            eb = RlEditbox(self.view.id())
            eb.edit(
                'Description',
                on_done,
                issue.description.replace('\r', ''),
                issue_id=issue_id
            )

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


class RedlimeChangeDescriptionDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        base_id = self.view.settings().get('base_id')
        issue_id = self.view.settings().get('issue_id')
        eb = RlEditbox(base_id)
        eb.layout_base()
        redmine = Redlime.connect()
        issue = redmine.issue.get(issue_id)
        issue.description = text
        issue.save()
        eb.view.run_command('redlime_fetcher', {'issue_id': issue_id})

