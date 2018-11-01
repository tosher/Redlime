#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import utils


class RedlimeMagicEnterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # If line selection is off, can't parse lines, turn on unselectable mode
        is_unselectable = self.view.settings().get('redlime_issue_unselectable', True)
        if not is_unselectable:
            self.view.settings().set('redlime_issue_unselectable', True)
            self.view.sel().add(self.view.line(self.view.sel()[0].end()))

        header_pattern = '^##\s.*$'
        try:
            headers = self.view.find_all(header_pattern)
            selected = self.view.sel()[0]
            selected_header = max([h for h in headers if h.b < selected.b])
            selected_header_str = self.view.substr(selected_header).lstrip('# ')
        except Exception:
            pass

        if selected_header_str:

            if selected_header_str.startswith('SubIssues'):
                self.view.run_command('redlime_open_subissue')
            elif selected_header_str.startswith('Relations'):
                self.view.run_command('redlime_open_subissue')
            elif selected_header_str.startswith('Attachments'):
                self.view.run_command('redlime_open_link')
            elif selected_header_str.startswith('Description'):
                self.view.run_command('redlime_change_description')
            elif selected_header_str.startswith('Comments'):
                self.view.run_command('redlime_issue_add_comment')
            elif selected_header_str.startswith('Revision'):
                if self.view.substr(selected).lstrip(' ').startswith('['):
                    self.view.run_command('redlime_open_link')
            else:
                cols = utils.get_setting('issue_view_columns', [])
                colname = self.view.substr(selected).split('**')[1]
                col_prop = ''
                for col in cols:
                    if colname == col['colname']:
                        col_prop = col['prop']
                        if col['custom']:
                            self.view.run_command('redlime_change_custom_field')
                        else:
                            # TODO: any props..
                            if col_prop == 'id':
                                self.view.run_command('redlime_go_redmine')
                            elif col_prop == 'fixed_version':
                                self.view.run_command('redlime_version_issue')
                            elif col_prop == 'status':
                                self.view.run_command('redlime_set_status')
                            elif col_prop == 'tracker':
                                self.view.run_command('redlime_tracker_issue')
                            elif col_prop == 'project':
                                self.view.run_command('redlime_change_project')
                            elif col_prop == 'assigned_to':
                                self.view.run_command('redlime_set_assigned')
                            elif col_prop == 'priority':
                                self.view.run_command('redlime_priority_issue')
                            elif col_prop == 'done_ratio':
                                self.view.run_command('redlime_done_ratio_issue')
                            else:
                                sublime.message_dialog('Not implemented in this version')

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
