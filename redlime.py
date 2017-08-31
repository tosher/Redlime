import sublime
import sublime_plugin
import os
import sys
import webbrowser
import urllib

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))
from .libs.redmine import Redmine

BLOCK_LINE = '```\n'


def rl_get_setting(key, default_value=None):
    settings = sublime.load_settings('Redlime.sublime-settings')
    return settings.get(key, default_value)


def rl_get_safe(issue, value):
    try:
        # issue.version can raise exception if empty - convert to dict and get value safe
        return str(dict(issue).get(value, {}).get('name', ''))
    except:
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


def rl_validate_screen(screen_type):

    is_valid = sublime.active_window().active_view().settings().get(screen_type, False)
    if not is_valid:
        if screen_type == 'redlime_issue':
            sublime.message_dialog('This command is provided for the issue screen!')
        elif screen_type == 'redlime_query':
            sublime.message_dialog('This command is provided for the issues query!')
        else:
            sublime.message_dialog('This command is provided for Redlime view!')


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

### Issue commands ###


# View Issue
class RedlimeCommand(sublime_plugin.TextCommand):
    def run(self, edit, issue_id=None):
        if not issue_id:
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                issue_id = line.split('|')[1].strip()
                int(issue_id)  # check is number
            except:
                pass

        if not issue_id:
            issue_id = ''
            self.view.window().show_input_panel("Issue ID #:", issue_id, self.get_issue, None, None)
        else:
            self.get_issue(issue_id)

    def get_issue(self, text):
        self.view.run_command('redlime_fetcher', {'issue_id': text})


# Issue comment
class RedlimeCommentIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # validate
        rl_validate_screen('redlime_issue')

        self.view.window().show_input_panel("Comment #:", "", self.post_comment, None, None)

    def post_comment(self, text):
        self.view.run_command('redlime_post_comment', {'text': text})


# Issue version
class RedlimeVersionIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(idx):
            if idx >= 0:
                issue.fixed_version_id = project_version_ids[idx]
                issue.save()
                sublime.status_message('Version changed!')
                self.view.run_command('redlime_fetcher', {'issue_id': issue.id})

        # validate
        rl_validate_screen('redlime_issue')

        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            redmine = Redlime.connect()
            issue = redmine.issue.get(issue_id)
            project_versions = []
            project_version_ids = []
            for ver in issue.project.versions:
                project_versions.append(ver.name)
                project_version_ids.append(ver.id)

            sublime.set_timeout(lambda: self.view.window().show_quick_panel(project_versions, on_done), 1)


# Issue priority
class RedlimePriorityIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(idx):
            if idx >= 0:
                issue.priority_id = enums_ids[idx]
                issue.save()
                sublime.status_message('Priority changed!')
                self.view.run_command('redlime_fetcher', {'issue_id': issue.id})

        # validate
        rl_validate_screen('redlime_issue')

        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            redmine = Redlime.connect()
            issue = redmine.issue.get(issue_id)
            enumerations = redmine.enumeration.filter(resource='issue_priorities')
            enums = []
            enums_ids = []
            for enum in enumerations:
                enums.append(enum.name)
                enums_ids.append(enum.id)

            sublime.set_timeout(lambda: self.view.window().show_quick_panel(enums, on_done), 1)


# Issue refresh
class RedlimeRefreshIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            self.view.run_command('redlime_fetcher', {'issue_id': issue_id})
            sublime.status_message('Issue Refreshed!')


# Issue status
class RedlimeSetStatusCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(i):
            if i > -1:
                if issue_id != 0:
                    issue = redmine.issue.get(issue_id)
                    issue.status_id = statuses_ids[i]
                    issue.save()
                    sublime.status_message('Issue #%r now is %s' % (issue.id, statuses_names[i]))
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        # validate
        rl_validate_screen('redlime_issue')

        redmine = Redlime.connect()
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            statuses = redmine.issue_status.all()
            statuses_names = []
            statuses_ids = []
            for status in statuses:
                statuses_names.append(status.name)
                statuses_ids.append(status.id)

            self.view.window().show_quick_panel(statuses_names, on_done)


# Issue status
class RedlimeChangeProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(i):
            if i >= 0:
                if issue_id != 0:
                    issue = redmine.issue.get(issue_id)
                    issue.project_id = projects[i].id
                    issue.save()
                    sublime.status_message('Issue #%r is moved to %s' % (issue.id, projects[i].name))
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        # validate
        rl_validate_screen('redlime_issue')

        redmine = Redlime.connect()
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            projects_filter = rl_get_setting('projects_filter', [])
            if projects_filter:
                projects = [redmine.project.get(pid) for pid in projects_filter]
            else:
                projects = redmine.project.all()
            projects_names = [prj.name for prj in projects]

            self.view.window().show_quick_panel(projects_names, on_done)


# Issue custom field
class RedlimeChangeCustomFieldCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(text):
            if text:
                if issue_id and field_id:
                    value = rl_prepare_custom_value(redmine, field_type, field, issue_id, text)
                    issue.custom_fields = [{'id': field_id, 'value': value}]
                    issue.save()
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        # validate
        rl_validate_screen('redlime_issue')

        redmine = Redlime.connect()
        field_id = None
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            try:
                colname = self.view.substr(self.view.sel()[0]).split('**')[1]
            except:
                colname = ""

            if colname:
                col_prop = None
                cols = rl_get_setting('issue_view_columns', [])
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
                            value = rl_get_custom_value(redmine, field_type, field)
                            break

                if field_id:
                    self.view.window().show_input_panel("%s:" % colname, value, on_done, None, None)
                else:
                    sublime.message_dialog('Field "%s" is not custom field' % (colname))


# Issue subject
class RedlimeChangeSubjectCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(text):
            if text:
                if issue_id != 0:
                    issue.subject = text
                    issue.save()
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        # validate
        rl_validate_screen('redlime_issue')

        redmine = Redlime.connect()
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            issue = redmine.issue.get(issue_id)
            self.view.window().show_input_panel("Subject:", issue.subject, on_done, None, None)


# Issue description
class RedlimeChangeDescriptionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(text):
            if text:
                if issue_id != 0:
                    issue.description = text
                    issue.save()
                    self.view.run_command('redlime_fetcher', {'issue_id': issue_id})

        # validate
        rl_validate_screen('redlime_issue')

        redmine = Redlime.connect()
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            issue = redmine.issue.get(issue_id)
            self.view.window().show_input_panel("Description:", issue.description.replace('\r', ''), on_done, None, None)


# Issue Assigned To
class RedlimeSetAssignedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(index):
            if index >= 0:
                assigned_to_id = users[index].id
                issue.assigned_to_id = assigned_to_id
                issue.save()

                sublime.status_message('Issue #%r is assigned to %s!' % (issue.id, users_menu[index]))
                self.view.run_command('redlime_fetcher', {'issue_id': issue.id})

        # validate
        rl_validate_screen('redlime_issue')

        redmine = Redlime.connect()
        users = []
        users_menu = []
        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            issue = redmine.issue.get(issue_id)
            groups = rl_get_setting('assigned_to_group_id_filter', [])  # user group filter
            if groups:
                for group_id in groups:
                    for user in redmine.user.filter(group_id=group_id):
                        if user.id not in [user.id for user in users]:
                            users.append(user)
            else:
                project_id = issue.project.id
                users = [redmine.user.get(user.user.id) for user in redmine.project_membership.filter(project_id=project_id) if hasattr(user, 'user')]

            if users:
                for user in users:
                    users_menu.append('%s %s' % (user.firstname, user.lastname))
                sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(users_menu, on_done), 1)


# Issue done_ratio
class RedlimeDoneRatioIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(idx):
            if idx >= 0:
                issue.done_ratio = int(enums[idx])
                issue.save()
                sublime.status_message('Done ratio changed!')
                self.view.run_command('redlime_fetcher', {'issue_id': issue.id})

        # validate
        rl_validate_screen('redlime_issue')

        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            redmine = Redlime.connect()
            issue = redmine.issue.get(issue_id)
            # https://github.com/redmine/redmine/blob/3.4-stable/app/views/issues/_attributes.html.erb#L72
            enums = [str(10 * x) for x in range(0, 11)]

            sublime.set_timeout(lambda: self.view.window().show_quick_panel(enums, on_done), 1)


class RedlimeMagicEnterCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # validate
        rl_validate_screen('redlime_issue')

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
        except:
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
                self.view.run_command('redlime_comment_issue')
            elif selected_header_str.startswith('Revision'):
                if self.view.substr(selected).lstrip(' ').startswith('['):
                    self.view.run_command('redlime_open_link')
            else:
                # TODO: default values
                cols = rl_get_setting('issue_view_columns', [])
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


# Issue: Open in Browser
class RedlimeGoRedmineCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # validate
        rl_validate_screen('redlime_issue')

        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            url = '%s/issues/%s' % (rl_get_setting('redmine_url').rstrip('/'), issue_id)
            webbrowser.open(url)


# Issue: Comment add
class RedlimePostCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):

        # validate
        rl_validate_screen('redlime_issue')

        issue_id = self.view.settings().get('issue_id', None)
        if issue_id:
            redmine = Redlime.connect()

            issue = redmine.issue.get(issue_id)
            issue.notes = text
            issue.save()

            sublime.status_message('Comment posted!')
            self.view.run_command('redlime_fetcher', {'issue_id': issue.id})


# Issue: Open external wiki page (custom)
class RedlimeOpenWikiCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # validate
        rl_validate_screen('redlime_issue')

        field_prop = rl_get_setting('external_wiki_field', None)
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


# Issue: Open selected link: attachment, revision
class RedlimeOpenLinkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # validate
        rl_validate_screen('redlime_issue')

        url = self.view.substr(self.view.sel()[0]).split('(')[1].rstrip(')')
        if url:
            webbrowser.open(url)


class RedlimeToggleSelectableCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        is_unselectable = self.view.settings().get('redlime_issue_unselectable', True)
        if is_unselectable:
            self.view.settings().set('redlime_issue_unselectable', False)
        else:
            self.view.settings().set('redlime_issue_unselectable', True)


# Issue: Open selected SubIssue
class RedlimeOpenSubissueCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # validate
        rl_validate_screen('redlime_issue')

        issue_id = None

        try:
            issue_id = self.view.substr(self.view.sel()[0]).split(':')[0]
            int(issue_id)
        except:
            pass

        if issue_id:
            self.view.run_command('redlime', {'issue_id': issue_id})


class RedlimeFetcherCommand(sublime_plugin.TextCommand):
    def run(self, edit, issue_id):
        try:
            self.redlime_view(edit, issue_id)
        except:
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
            syntax_file = rl_get_setting('syntax_file', 'Packages/Redlime/Redlime.tmLanguage')
            r.set_syntax_file(syntax_file)

        cols = rl_get_setting('issue_view_columns', [])
        cols_maxlen = len(max([col['colname'] for col in cols], key=len)) + 5  # +4* +1

        issue = self.redmine.issue.get(issue_id)
        r.settings().set('redlime_issue', True)
        r.settings().set('issue_id', issue.id)

        cols_data = []
        line_format = '\t{:<%s}: {:<}' % cols_maxlen
        for col in cols:
            value = None
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
                        value = rl_get_custom_value(self.redmine, field_type, field)
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
            '[a](assign to)',
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
                    comments += '\t*(%s)*\n' % rl_get_datetime(journal.created_on)
                    comments += BLOCK_LINE
        if comments:
            content += '\n'
            content += '## Comments\n'
            content += comments

        if issue.changesets:
            content += '## Revisions\n'
            content += BLOCK_LINE
            for chset in issue.changesets:
                redmine_url = rl_get_setting('redmine_url')
                project = self.redmine.project.get(issue.project.id)
                chset_url = '%s/projects/%s/repository/revisions/%s' % (redmine_url.rstrip('/'), project.identifier, chset['revision'])
                content += '\t[%s](%s)\n\t**Comment**: %s *(%s)*\n' % (chset['user']['name'], chset_url, chset['comments'], rl_get_datetime(chset['committed_on']))
            content += BLOCK_LINE
            content += '\n'

        r.insert(edit, 0, content)
        r.set_name("Issue #%s" % issue_id)
        r.set_read_only(True)

### Issues lists ###


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


# Queries list
class RedlimeGetQueryCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(i):
            if i > -1:
                query = query_ids[i]
                project_id = query_projects[i]
                self.view.run_command('redlime_fetch_query', {'project_id': project_id, 'query_id': query, 'query_project_name': query_names[i]})

        redmine = Redlime.connect()
        projects_filter = rl_get_setting('projects_filter', [])
        if projects_filter:
            projects = [redmine.project.get(pid) for pid in projects_filter]
        else:
            projects = redmine.project.all()

        queries = redmine.query.all()
        query_names = []
        query_ids = []
        query_projects = []
        for query in queries:
            if hasattr(query, 'project_id'):
                if query.project_id in [prj.id for prj in projects]:
                    project = redmine.project.get(query.project_id)
                    query_projects.append(query.project_id)
                    query_names.append([query.name, project.name])
                    query_ids.append(query.id)

        self.view.window().show_quick_panel(query_names, on_done)


# Issues by project
class RedlimeProjectIssuesCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        redmine = Redlime.connect()
        projects_filter = rl_get_setting('projects_filter', [])
        if projects_filter:
            projects = [redmine.project.get(pid) for pid in projects_filter]
        else:
            projects = redmine.project.all()

        self.prj_names = []
        self.prj_ids = []
        for prj in projects:
            self.prj_names.append(prj.name)
            self.prj_ids.append(prj.id)
        self.view.window().show_quick_panel(self.prj_names, self.on_done)

    def on_done(self, idx):
        if idx >= 0:
            title = 'Issues: %s' % self.prj_names[idx]
            limit = rl_get_setting('query_page_size', 40)
            query_params = {'project_id': self.prj_ids[idx], 'title': title, 'limit': limit, 'offset': 0, 'page_number': 1}
            text = rl_show_cases(**query_params)
            r = self.view.window().new_file()
            r.set_name(title)
            syntax_file = rl_get_setting('syntax_file', 'Packages/Redlime/Redlime.tmLanguage')
            r.set_syntax_file(syntax_file)
            r.settings().set('query_params', query_params)
            r.settings().set('redlime_query', True)
            r.settings().set("word_wrap", False)
            r.run_command('redlime_insert_text', {'position': 0, 'text': text})
            r.set_scratch(True)
            r.set_read_only(True)


# Projects issues filter by "Assigned to"
class RedlimeAssignFilterCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        # validate
        rl_validate_screen('redlime_query')

        self.users = []
        self.users_menu = ['*All users']
        redmine = Redlime.connect()
        groups = rl_get_setting('assigned_to_group_id_filter', [])  # user group filter
        if groups:
            for group_id in groups:
                for user in redmine.user.filter(group_id=group_id):
                    if user.id not in [user.id for user in self.users]:
                        self.users.append(user)
        else:
            query_params = self.view.settings().get('query_params', {})
            project_id = query_params.get('project_id')
            # self.users = [redmine.user.get(user.user.id) for user in redmine.project_membership.filter(project_id=project_id) if hasattr(user, 'user')]
            self.users = [user.user for user in redmine.project_membership.filter(project_id=project_id) if hasattr(user, 'user')]

        if self.users:
            for user in self.users:
                # self.users_menu.append('%s %s' % (user.firstname, user.lastname))
                self.users_menu.append(user.name)
            self.view.window().show_quick_panel(self.users_menu, self.on_done)

    def on_done(self, idx):
        query_params = self.view.settings().get('query_params', {})
        limit = rl_get_setting('query_page_size', 40)
        query_params['limit'] = limit
        query_params['offset'] = 0
        query_params['page_number'] = 1
        if idx == 0:
            query_params.pop('assigned_to_id', None)
            self.view.settings().set('query_params', query_params)
        elif idx > 0:
            query_params['assigned_to_id'] = self.users[idx - 1].id
            self.view.settings().set('query_params', query_params)
        self.view.run_command('redlime_issues_refresh')


# Issues refresh
class RedlimeIssuesRefreshCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # validate
        rl_validate_screen('redlime_query')

        query_params = self.view.settings().get('query_params')
        limit = rl_get_setting('query_page_size', 40)
        query_params['limit'] = limit
        if query_params:
            text = rl_show_cases(**query_params)
            self.view.set_read_only(False)
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            self.view.run_command('redlime_insert_text', {'position': 0, 'text': text})
            self.view.set_read_only(True)


# Issues next page
class RedlimeIssuesPageCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction):

        # validate
        rl_validate_screen('redlime_query')

        query_params = self.view.settings().get('query_params')
        limit = rl_get_setting('query_page_size', 40)
        offset = query_params.get('offset', 0)
        page_number = query_params.get('page_number', 1)
        if direction:
            offset_new = offset + limit
            page_number = page_number + 1
        else:
            offset_new = offset - limit
            offset_new = offset_new if offset_new >= 0 else 0
            page_number = page_number - 1
            page_number = page_number if page_number >= 1 else 1
        query_params['page_number'] = page_number
        query_params['offset'] = offset_new
        query_params['limit'] = limit
        self.view.settings().set('query_params', query_params)

        if query_params:
            text = rl_show_cases(**query_params)
            self.view.set_read_only(False)
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            self.view.run_command('redlime_insert_text', {'position': 0, 'text': text})
            self.view.set_read_only(True)


# Issues list by query
class RedlimeFetchQueryCommand(sublime_plugin.TextCommand):
    def run(self, edit, project_id, query_id, query_project_name):
        r = self.view.window().new_file()
        title = '%s (%s)' % (query_project_name[0], query_project_name[1])
        r.set_name(title)
        r.set_scratch(True)
        syntax_file = rl_get_setting('syntax_file', 'Packages/Redlime/Redlime.tmLanguage')
        r.set_syntax_file(syntax_file)
        limit = rl_get_setting('query_page_size', 40)
        page_number = 1
        query_params = {'project_id': project_id, 'query_id': query_id, 'title': title, 'limit': limit, 'offset': 0, 'page_number': page_number}
        content = rl_show_cases(**query_params)
        r.settings().set('query_params', query_params)
        r.settings().set('redlime_query', True)

        r.settings().set("word_wrap", False)
        r.run_command('redlime_insert_text', {'position': 0, 'text': content})
        r.set_read_only(True)


### Events ###
class RedlimeLoad(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        is_redlime_query = view.settings().get('redlime_query', False)
        is_redlime_view_unselectable = view.settings().get('redlime_issue', False) and view.settings().get('redlime_issue_unselectable', True)
        # print(is_redlime_view_unselectable)

        if view.is_read_only() and (is_redlime_query or is_redlime_view_unselectable):
            view.sel().add(view.line(view.sel()[0].end()))
