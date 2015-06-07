## Redlime: SublimeText 3 Redmine Client

SublimeText Plugin to interact with Redmine right in your editor. Based on another plugin: [SubRed](https://packagecontrol.io/packages/SubRed)

## Install

### Package Control
The easiest way to install this is with [Package Control](http://wbond.net/sublime\_packages/package\_control).

 * If you just went and installed Package Control, you probably need to restart Sublime Text before doing this next bit.
 * Bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows).
 * **Temporary!** Select "Package Control: Add Repository" and add
 ```
 https://github.com/tosher/Redlime.git
 ```
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select TSQL Easy when the list appears.

Package Control will automatically keep **Redlime** up to date with the latest version.

### Configure

##### Basic
* Set the *redmine_url* and *api_key* in *Preferences: Package Settings > SubRed > Settings – User*.
* Configure the *issue_list_columns* and *issue_view_columns* for showing issues as you want.
* Set the *projects_filter* and *assigned_to_group_id_filter* for filtering data for your projects only.

Example:

```
{
  "redmine_url" : "URL to your Redmine",
  "api_key": "Set your Redmine API Key",
    "projects_filter": ["my_project_short_name", "my_another_project_short_name"],
    "assigned_to_group_id_filter": 17,
    "syntax_file": "Packages/Redlime/Redlime.tmLanguage",
    "issue_list_columns": [
        { "prop": "id", "colname": "#", "custom": false, "align": "right" },
        { "prop": "fixed_version", "colname": "Version", "custom": false},
        { "prop": "Build", "colname": "Build", "custom": true},
        { "prop": "tracker", "colname": "Type", "custom": false},
        { "prop": "priority", "colname": "Prior.", "custom": false},
        { "prop": "status", "colname": "Status", "custom": false},
        { "prop": "assigned_to", "colname": "Assigned", "custom": false},
        { "prop": "subject", "colname": "Subject", "custom": false, "maxlen": 80}
    ],
    "issue_view_columns": [
        { "prop": "id", "colname": "Issue", "custom": false},
        { "prop": "project", "colname": "Project", "custom": false},
        { "prop": "fixed_version", "colname": "Version", "custom": false},
        { "prop": "status", "colname": "Status", "custom": false},
        { "prop": "priority", "colname": "Priority", "custom": false},
        { "prop": "author", "colname": "Author", "custom": false},
        { "prop": "assigned_to", "colname": "Assigned to", "custom": false},
        { "prop": "created_on", "colname": "Creation date", "custom": false, "type": "datetime"},
        { "prop": "Build", "colname": "Build", "custom": true}
    ]
}
```

### Available commands:

#### Issues list commands
* Redlime: Project issues
* Redlime: List queries
* Redlime: Refresh issues
* Redlime: Assign filter

#### Hotkeys 
[Enter] *view issue* [r] *refresh issues* [a] *assign filter*

#### Issue view/edit commands
* Redlime: View issue
* Redlime issue: Refresh
* Redlime issue: Post comment
* Redlime issue: Change version
* Redlime issue: Set status
* Redlime issue: Change project
* Redlime issue: Change subject
* Redlime issue: Assign to
* Redlime issue: Change priority
* Redlime issue: Open in browser
* Redlime issue: Open selected attachment
* Redlime issue: Change description
* Redlime issue: Open selected issue
* Redlime issue: Change selected custom field
* Redlime issue: Open external wiki

#### Hotkeys 
[f2] *change subject* [c] *post a comment* [s] *change state* [v] *change version* [b] *change custom field*              
[a] *assing to* [p] *change priority* [m] *move to project* [r] *refresh issue* [g] *open in browser*           
[w] *open wiki* [f] *open selected attachment* [d] *change description* [i] *open selected issue*       
