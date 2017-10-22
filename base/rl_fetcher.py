#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import urllib
import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime

BLOCK_LINE = '```\n'


class RedlimeFetcherCommand(sublime_plugin.TextCommand):
    def run(self, edit, issue_id):
        try:
            self.redlime_view(edit, issue_id)
        except Exception:
            sublime.status_message('Issue #%s not found!' % (issue_id))

    def redlime_view(self, edit, issue_id):

        def get_maxlen(values):
            return len(max(values, key=len))

        def rl_pretty(value, lenght):
            if len(str(value)) > lenght:
                return value
            else:
                return '%s%s' % (value, ' ' * (lenght - len(str(value))))

        self.redmine = Redlime.connect()
        issue_current_id = self.view.settings().get('issue_id', None)
        if issue_current_id == issue_id:
            r = self.view
            r.set_read_only(False)
            r.erase(edit, sublime.Region(0, self.view.size()))
        else:
            r = sublime.active_window().new_file()
            r.set_scratch(True)
            syntax_file = utils.rl_get_setting('syntax_file', 'Packages/Redlime/Redlime.tmLanguage')
            r.set_syntax_file(syntax_file)

        cols = utils.rl_get_setting('issue_view_columns', [])
        cols_maxlen = len(max([col['colname'] for col in cols], key=len)) + 5  # +4* +1

        issue = self.redmine.issue.get(issue_id)
        r.settings().set('screen', 'redlime_issue')
        r.settings().set('redlime_issue_unselectable', True)
        r.settings().set('issue_id', issue.id)

        cols_data = []
        line_format = '\t{:<%s}: {:<}' % cols_maxlen
        for col in cols:
            value = None
            field_type = col.get('type', None)
            col_prop = col['prop']
            if not col['custom']:
                value = utils.rl_get_safe(issue, col_prop)
                if field_type == 'datetime':
                    value = utils.rl_get_datetime(value)
                elif field_type == 'percentage':
                    value = utils.rl_get_percentage(value)
                elif field_type == 'progressbar':
                    value = utils.rl_get_progressbar(value)
            elif hasattr(issue, 'custom_fields'):
                for field in issue.custom_fields:
                    if field['name'] == col_prop:
                        value = utils.rl_get_custom_value(self.redmine, field_type, field)
                        break

            if value is not None:
                line = line_format.format('**%s**' % col['colname'], value)
                cols_data.append(line)

        cols_data_print = '\n'.join(cols_data)

        header_print = '## %s\n' % (issue.subject)

        shortcuts = [
            '[f2](change subject)',
            '[c](post a comment)',
            '[s](change state)',
            '[v](change version)',
            '[b](change custom field)',
            '[a](assing to)',
            '[p](change priority)',
            '[%](change done ratio)',
            '[m](move to project)',
            '[r](refresh issue)',
            '[g](open in browser)',
            '[w](open external wiki)',
            '[l](open selected link)',
            '[d](change description)',
            '[i](open selected issue)',
            '[u](toggle select mode)',
            '[Enter](*magic)']

        shortcuts_print = ''
        maxlen = len(max(shortcuts, key=len)) + 2

        for idx, s in enumerate(shortcuts):
            idx += 1
            line_format = '{:<%s}\n' % (maxlen) if not idx % 5 else '{:<%s}' % maxlen
            shortcuts_print += line_format.format(s)

        content = ''
        content += shortcuts_print
        content += '\n'
        content += '\n'
        content += header_print
        content += '\n'
        content += BLOCK_LINE
        content += cols_data_print
        content += '\n'
        content += BLOCK_LINE
        content += '\n'

        if issue.children:
            content += '## SubIssues\n'
            content += BLOCK_LINE
            try:
                for child in issue.children:
                    content += '\t%s: **%s**\n' % (child.id, child.subject)
            except Exception as e:
                print(e)
            content += BLOCK_LINE
            content += '\n'

        if issue.relations:
            content += '## Relations\n'
            content += BLOCK_LINE
            try:
                for rel in issue.relations:
                    content += '\t%s: **%s**\n' % (rel.issue_to_id, rel.relation_type)
            except Exception as e:
                print(e)
            content += BLOCK_LINE
            content += '\n'

        if issue.attachments:
            content += '## Attachments\n'
            content += BLOCK_LINE
            for f in issue.attachments:
                content += '\t[%s](%s)\n' % (f.filename, urllib.parse.unquote(f.content_url))
            content += BLOCK_LINE
            content += '\n'

        content += '## Description\n'
        content += BLOCK_LINE
        content += '\t%s\n' % issue.description.replace('\r', '').replace('\n', '\n\t')
        content += BLOCK_LINE

        comments = ''
        for journal in issue.journals:
            if hasattr(journal, 'notes'):
                if journal.notes != '':
                    comments += '### %s\n' % (journal.user)
                    comments += BLOCK_LINE
                    comments += '\t%s\n' % journal.notes.replace('\r', '').replace('\n', '\n\t')
                    comments += '\t*(%s)*\n' % utils.rl_get_datetime(journal.created_on)
                    comments += BLOCK_LINE
        if comments:
            content += '\n'
            content += '## Comments\n'
            content += comments

        if issue.changesets:
            content += '## Revisions\n'
            content += BLOCK_LINE
            for chset in issue.changesets:
                redmine_url = utils.rl_get_setting('redmine_url')
                project = self.redmine.project.get(issue.project.id)
                chset_url = '%s/projects/%s/repository/revisions/%s' % (redmine_url.rstrip('/'), project.identifier, chset['revision'])
                content += '\t[%s](%s)\n\t**Comment**: %s *(%s)*\n' % (chset['user']['name'], chset_url, chset['comments'], utils.rl_get_datetime(chset['committed_on']))
            content += BLOCK_LINE
            content += '\n'

        r.insert(edit, 0, content)
        r.set_name("Issue #%s" % issue_id)
        r.set_read_only(True)

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