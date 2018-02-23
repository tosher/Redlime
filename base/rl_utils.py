#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
from collections import OrderedDict
import sublime
import sublime_plugin
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
from ..libs.redmine import Redmine
from ..libs.terminaltables.other_tables import WindowsTable as SingleTable

TABLE_SEP = '│'


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
        return '%02s%%' % percentage


def rl_get_progressbar(percentage):
    n = int(int(percentage) / 10)
    positive = rl_get_setting('progress_bar_positive_char', '+') * n
    negative = rl_get_setting('progress_bar_negative_char', '-') * (10 - n)
    return '%s%s %s%%' % (positive, negative, percentage)


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


def rl_get_issue_column_value(redmine, col, issue):
    value = ''
    col_type = col.get('type', None)
    if not col['custom']:
        value = rl_get_safe(issue, col['prop'])
        if col_type == 'datetime':
            value = rl_get_datetime(value)
        elif col_type == 'percentage':
            value = rl_get_percentage(value)
        elif col_type == 'progressbar':
            value = rl_get_progressbar(value)
    elif hasattr(issue, 'custom_fields'):
        for field in issue.custom_fields:
            if field['name'] == col['prop']:
                value = rl_get_custom_value(redmine, col_type, field)
                break
    return value


def rl_get_issues_header(title, count, page_number):
    content_header = '\n## %s\n\n' % title
    content_header += 'Total: %s\n' % count
    content_header += 'Page number: %s\n\n' % page_number
    return content_header


def rl_show_issues(title, **kwargs):
    content = ''
    redmine = Redlime.connect()
    issues = redmine.issue.filter(**kwargs)

    cols = rl_get_setting('issue_list_columns', {})
    tbl_header = [col['colname'] for col in cols]
    table_data = [tbl_header]
    content += rl_get_issues_header(title, len(issues), kwargs.get('page_number', 1))

    if not issues:
        return content + SingleTable([["Issues not found"]]).table

    for issue in issues:
        issue_cols = []
        for col in cols:
            value = rl_get_issue_column_value(redmine, col, issue)
            issue_cols.append(value)
        table_data.append(issue_cols)

    objects_table = SingleTable(table_data)
    return content + objects_table.table


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

shortcuts_issue_list_query = OrderedDict([
    ('new', ['n', 'new issue']),
    ('edit', ['Enter', 'edit issue']),
    ('refresh', ['r', 'refresh issues']),
    ('ppage', [rl_get_setting('char_left_arrow'), 'prev. page']),
    ('npage', [rl_get_setting('char_right_arrow'), 'next page'])
])

cols_issue_list_query = [
    ['new'],
    ['edit'],
    ['refresh'],
    ['ppage'],
    ['npage']
]

shortcuts_issue_list_project = shortcuts_issue_list_query.copy()
shortcuts_issue_list_project['assign'] = ['a', 'assign filter']

cols_issue_list_project = cols_issue_list_query[:]
cols_issue_list_project.insert(3, ['assign'])

shortcuts_issue_edit = OrderedDict([
    ('subject', ['F2', 'change subject']),
    ('comment', ['c', 'new comment']),
    ('state', ['s', 'change state']),
    ('version', ['v', 'change version']),
    ('custom', ['b', 'change custom field']),
    ('assign', ['a', 'assign to']),
    ('priority', ['p', 'change priority']),
    ('ratio', ['%', 'change done ratio']),
    ('project', ['m', 'move to project']),
    ('refresh', ['r', 'refresh issue']),
    ('browser', ['g', 'open in browser']),
    ('wiki', ['w', 'open external wiki']),
    ('link', ['l', 'open selected link']),
    ('descr', ['d', 'change description']),
    ('issue', ['i', 'open selected issue']),
    ('mode', ['u', 'toggle select mode']),
    ('any', ['Enter', 'change any'])
])

cols_issue_edit = [
    ['refresh', 'subject', 'descr'],
    ['comment', 'ratio', 'assign'],
    ['state', 'version', 'priority'],
    ['project', 'custom', 'any'],
    ['ratio', 'mode', 'wiki'],
    ['browser', 'link', 'issue']
]
