#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import utils
from .utils import Redlime
from .editbox import Editbox


class RedlimeIssueAddCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        on_done = 'redlime_issue_add_comment_done'
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            # redmine = Redlime.connect()
            # issue = redmine.issue.get(issue_id)
            eb = Editbox(self.view.id())
            eb.edit(
                'Comment',
                on_done,
                '',
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


class RedlimeIssueAddCommentDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, obj_kwargs):
        issue_id = self.view.settings().get('issue_id')
        redmine = Redlime.connect()
        issue = redmine.issue.get(issue_id)
        issue.notes = text
        issue.save()
        self.view.window().status_message('Comment posted!')
        self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

