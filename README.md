## Redlime: SublimeText 3 Redmine manager

SublimeText 3 plugin to manage Redmine issues. 
Concept idea based on another plugin (fork): [SubRed](https://packagecontrol.io/packages/SubRed), but with many differences and improvements:

 * Fully customizable issue fields - default and custom.
 * Create new issues.
 * Edit all issue properties.
 * Show/open issue dependencies, subissues, attachments.
 * Redmine project as main path to issues (queries are supported too).
 * With improved interface and improved highlighting based on own syntax (or possible to use markdown themes).

## Screenshots

Project issues list:
![Redlime - project issues](https://raw.githubusercontent.com/wiki/tosher/Redlime/redlime_issues.png)

Issue:
![Redlime - project issue](https://raw.githubusercontent.com/wiki/tosher/Redlime/redlime_issue.png)

## Install

### Package Control
The easiest way to install this is with [Package Control](http://wbond.net/sublime\_packages/package\_control).

 * If you just went and installed Package Control, you probably need to restart Sublime Text before doing this next bit.
 * Bring up the Command Palette (<kbd>Command+Shift+p</kbd> on OS X, <kbd>Control+Shift+p</kbd> on Linux/Windows).
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select Redlime when the list appears.

Package Control will automatically keep **Redlime** up to date with the latest version.

### Configure

##### Basic
 * Open plugin settings *Preferences: Package Settings > Redlime > Settings – User*.
 * Set the *redmine_url* and *api_key*.
 * Configure the *issue_list_columns* and *issue_view_columns* for showing issues as you want.
 * Set the *projects_filter* and *assigned_to_group_id_filter* for filtering data for your projects only.

Example:

```json
{
    "redmine_url" : "URL to your Redmine",
    "api_key": "Set your Redmine API Key",
    "projects_filter": ["my_project_short_name", "my_another_project_short_name"],
    "assigned_to_group_id_filter": [17],
    "query_page_size": 40,
    "syntax_file": "Packages/Redlime/Redlime.tmLanguage",
    "issue_list_columns": [
        { "prop": "id", "colname": "#", "custom": false, "align": "right" },
        { "prop": "fixed_version", "colname": "Version", "custom": false},
        { "prop": "Build", "colname": "Build", "custom": true},
        { "prop": "tracker", "colname": "Type", "custom": false},
        { "prop": "priority", "colname": "Prior.", "custom": false},
        { "prop": "status", "colname": "Status", "custom": false},
        { "prop": "assigned_to", "colname": "Assigned", "custom": false},
        { "prop": "subject", "colname": "Subject", "custom": false, "maxlen": 80},
        { "prop": "done_ratio", "colname": "% Done", "custom": false, "type": "progressbar"},
    ],
    "issue_view_columns": [
        { "prop": "id", "colname": "Issue", "custom": false},
        { "prop": "project", "colname": "Project", "custom": false},
        { "prop": "fixed_version", "colname": "Version", "custom": false},
        { "prop": "status", "colname": "Status", "custom": false},
        { "prop": "priority", "colname": "Priority", "custom": false},
        { "prop": "done_ratio", "colname": "Done ratio", "custom": false, "type": "percentage"},
        { "prop": "author", "colname": "Author", "custom": false},
        { "prop": "assigned_to", "colname": "Assigned to", "custom": false},
        { "prop": "created_on", "colname": "Creation date", "custom": false, "type": "datetime"},
        { "prop": "Build", "colname": "Build", "custom": true}
    ]
}
```

### Plugin commands:

#### Issues list commands
* Redlime: Project issues
* Redlime: List queries
* <kbd>r</kbd> Redlime: Refresh issues
* <kbd>a</kbd> Redlime: Assign filter - for project issues only
* <kbd>&#8592;</kbd> Redlime: Previous page
* <kbd>&#8594;</kbd> Redlime: Next page
* <kbd>Enter</kbd> Redlime: View issue

#### Issue view/edit commands
* <kbd>r</kbd> Redlime issue: Refresh
* <kbd>c</kbd> Redlime issue: Post comment
* <kbd>v</kbd> Redlime issue: Change version
* <kbd>s</kbd> Redlime issue: Set status
* <kbd>m</kbd> Redlime issue: Change project
* <kbd>F2</kbd> Redlime issue: Change subject
* <kbd>a</kbd> Redlime issue: Assign to
* <kbd>p</kbd> Redlime issue: Change priority
* <kbd>%</kbd> Redlime issue: Change done ratio
* <kbd>g</kbd> Redlime issue: Open in browser
* <kbd>l</kbd> Redlime issue: Open selected link
* <kbd>d</kbd> Redlime issue: Change description
* <kbd>i</kbd> Redlime issue: Open selected issue
* <kbd>b</kbd> Redlime issue: Change selected custom field
* <kbd>w</kbd> Redlime issue: Open external wiki
* <kbd>Enter</kbd> Redlime issue: Magic enter - run issue command by selected line
* <kbd>u</kbd> Redlime issue: Toggle select mode - toggle full-line selection mode for possibility to copy any selected text.
