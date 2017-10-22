#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
import sublime
import sublime_plugin
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
from ..libs.redmine import Redmine


object_commands = {
    'issue': {
        'char': '#',
        'screen_view': 'redlime_issue',
        'screen_list': 'redlime_query'
        # 'view': 'st_gitlab_issue',
        # 'list': 'st_gitlab_project_issues_list',
        # 'fetch': 'st_gitlab_issue_fetcher'
    }
}


class Redlime:
    def connect():
        settings = sublime.load_settings("Redlime.sublime-settings")
        url = settings.get('redmine_url')
        api_key = settings.get('api_key')
        requests = settings.get('connection_options')

        # datetime format
        # http://python-redmine.readthedocs.org/en/latest/configuration.html#datetime-formats
        return Redmine(url, key=api_key, datetime_format='%Y-%m-%dT%H:%M:%SZ', requests=requests)


class RedlimeInsertTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, position, text):
        self.view.insert(edit, position, text)


def rl_get_setting(key, default_value=None):
    settings = sublime.load_settings('Redlime.sublime-settings')
    return settings.get(key, default_value)


def rl_get_safe(issue, value):
    try:
        # issue.version can raise exception if empty - convert to dict and get value safe
        return str(dict(issue).get(value, {}).get('name', ''))
    except Exception:
        return str(dict(issue).get(value, ''))


def rl_get_datetime(datetime_str):
    try:
        return datetime_str.strftime("%d.%m.%Y %H:%M:%S")
    except AttributeError:
        return datetime_str.replace('T', ' ').replace('Z', '')


def rl_get_percentage(percentage):
    if percentage == '100':
        return '100%'
    else:
        return '%02s %%' % percentage


def rl_get_progressbar(percentage):
    n = int(int(percentage) / 10)
    positive = '█' * n
    negative = '░' * (10 - n)
    return '%s%s' % (positive, negative)


def rl_get_custom_value(redmine, field_type, field):
    if field_type == 'version' and isinstance(field['value'], list):
        return ', '.join(redmine.version.get(ver).name for ver in field['value'])
    elif isinstance(field['value'], list):
        return ', '.join(val for val in field['value'])
    else:
        return str(field['value'])


def rl_prepare_custom_value(redmine, field_type, field, issue_id, value):
    if field_type == 'version' and isinstance(field['value'], list):
        issue = redmine.issue.get(issue_id)
        versions = []
        for ver_str in value.split(','):
            ver_str = ver_str.strip()
            for ver in issue.project.versions:
                if ver.name == ver_str:
                    versions.append(ver.id)
        return versions
    elif isinstance(field['value'], list):
        return [val.strip() for val in value.split(',')]
    elif isinstance(field['value'], int):
        return int(value)
    else:
        return value


# def rl_validate_screen(screen):
#     is_valid = sublime.active_window().active_view().settings().get(screen, False)
#     if not is_valid:
#         if screen == 'redlime_issue':
#             sublime.message_dialog('This command is provided for the issue screen!')
#         elif screen == 'redlime_query':
#             sublime.message_dialog('This command is provided for the issues query!')
#         else:
#             sublime.message_dialog('This command is provided for Redlime view!')

def rl_show_cases(**kwargs):

    def get_data():
        cols_data = {}

        for col in cols:
            cols_data[col['prop']] = len(col['colname'])

        if cols:
            for issue in issues:
                for col in cols:

                    value = ''
                    maxlen = col.get('maxlen', None)
                    field_type = col.get('type', None)
                    col_prop = col['prop']

                    if not col['custom']:
                        value = rl_get_safe(issue, col_prop)
                        if field_type == 'datetime':
                            value = rl_get_datetime(value)
                        elif field_type == 'percentage':
                            value = rl_get_percentage(value)
                        elif field_type == 'progressbar':
                            value = rl_get_progressbar(value)
                    elif hasattr(issue, 'custom_fields'):
                        for field in issue.custom_fields:
                            if field['name'] == col_prop:
                                value = rl_get_custom_value(redmine, field_type, field)
                                break
                    value_len = len(cut(value, maxlen))
                    if value_len > cols_data[col_prop]:
                        cols_data[col_prop] = value_len
        return cols_data

    def cut(val, maxlen):
        if maxlen:
            if len(val) > maxlen:
                return '%s..' % val[:maxlen - 2].strip()
        return val

    def pretty(value, length, align='left'):

        align_sign = '<'
        if align == 'left':
            align_sign = '<'
        elif align == 'center':
            align_sign = '^'
        elif align == 'right':
            align_sign = '>'

        line_format = '{:%s%s}' % (align_sign, length)
        return line_format.format(value)

    def get_subline(lenval):
        # lenval + 2 spaces in column
        return '-' * (lenval + 2)

    redmine = Redlime.connect()
    cols = rl_get_setting('issue_list_columns', {})
    if cols:
        content = ''
        redmine = Redlime.connect()

        shortcuts = [
            '[Enter](view issue)',
            '[r](refresh issues)',
            '[<-](prev. page)',
            '[->](next page)']

        if not kwargs.get('query_id', None):
            shortcuts.append('[a](assign filter)')

        content_header = '%s\n\n' % ' '.join(shortcuts)
        if kwargs.get('title', None):
            content_header += '## %s\n' % kwargs['title']
            kwargs.pop("title", None)  # hack: title is not query param

        kwargs['status_id'] = 'open'  # force filter opened issues
        issues = redmine.issue.filter(**kwargs)

        content_header += 'Total: %s\n' % len(issues)
        content_header += 'Page number: %s\n\n' % kwargs.get('page_number', 1)

        table_data_widths = get_data()
        content_header_line = '%s-\n' % ('-' * (sum([val for key, val in table_data_widths.items()]) + len(cols) * 3))
        table_header = '| ' + ' | '.join(pretty(col['colname'], table_data_widths[col['prop']], 'center') for col in cols)
        table_header = '%s |\n' % table_header

        if issues:
            for issue in issues:
                table_row = '|'
                for col in cols:

                    value = ''
                    maxlen = col.get('maxlen', None)
                    field_type = col.get('type', None)
                    col_prop = col['prop']

                    if not col['custom']:
                        value = rl_get_safe(issue, col_prop)
                        if field_type == 'datetime':
                            value = rl_get_datetime(value)
                        elif field_type == 'percentage':
                            value = rl_get_percentage(value)
                        elif field_type == 'progressbar':
                            value = rl_get_progressbar(value)
                    elif hasattr(issue, 'custom_fields'):
                        for field in issue.custom_fields:
                            if field['name'] == col_prop:
                                value = rl_get_custom_value(redmine, field_type, field)
                                break

                    value = cut(value, maxlen)
                    align = col.get('align', 'left')
                    table_row += ' %s |' % pretty(value, table_data_widths[col_prop], align)
                table_row += '\n'
                content += table_row
        else:
            text = 'No data'
            line_format = '|{:^%s}|\n' % (len(content_header_line) - 3)
            content += line_format.format(text)

        content_footer_line = content_header_line.replace('|', '-')
        return content_header + content_header_line + table_header + content_header_line + content + content_footer_line
