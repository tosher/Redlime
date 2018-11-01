#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import utils
from .utils import Redlime


class RedlimeChangeCustomFieldCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(text):
            if text:
                if issue_id and field_id:
                    value = utils.rl_prepare_custom_value(redmine, field_type, field, issue_id, text)
                    issue.custom_fields = [{'id': field_id, 'value': value}]
                    issue.save()
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        redmine = Redlime.connect()
        field_id = None
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            try:
                colname = self.view.substr(self.view.sel()[0]).split('**')[1]
            except Exception:
                colname = ""

            if colname:
                col_prop = None
                cols = utils.get_setting('issue_view_columns', [])
                for col in cols:
                    if colname == col['colname']:
                        col_prop = col['prop']
                        break

                if col_prop:
                    issue = redmine.issue.get(issue_id)
                    for field in issue.custom_fields:
                        if field['name'] == col_prop:
                            field_type = col.get('type', None)
                            field_id = field.id
                            value = utils.rl_get_custom_value(redmine, field_type, field)
                            break

                if field_id:
                    self.view.window().show_input_panel("%s:" % colname, value, on_done, None, None)
                else:
                    sublime.message_dialog('Field "%s" is not custom field' % (colname))

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
