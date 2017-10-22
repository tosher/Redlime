#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import rl_utils as utils
from .rl_utils import Redlime


class RedlimeGetQueryCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(i):
            if i > -1:
                query = query_ids[i]
                project_id = query_projects[i]
                self.view.run_command('redlime_fetch_query', {'project_id': project_id, 'query_id': query, 'query_project_name': query_names[i]})

        redmine = Redlime.connect()
        projects_filter = utils.rl_get_setting('projects_filter', [])
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
