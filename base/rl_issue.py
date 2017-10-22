#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin


class RedlimeIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit, issue_id=None):
        if not issue_id:
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                issue_id = line.split('|')[1].strip()
                int(issue_id)  # check is number
            except Exception:
                pass

        if not issue_id:
            issue_id = ''
            self.view.window().show_input_panel("Issue ID #:", issue_id, self.get_issue, None, None)
        else:
            self.get_issue(issue_id)

    def get_issue(self, issue_id):
        self.view.run_command('redlime_fetcher', {'issue_id': issue_id})
