# Copyright 2023 Clement L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil
from datetime import datetime

from git import Repo

import config


class Git:
    def __init__(self, path):
        self.path = path
        self.repo: None | Repo = None
        self.branch = None

        if not self.valid_directory():
            raise Exception("Invalid directory")

    def valid_directory(self):
        try:
            self.repo = Repo(self.path)
            self.branch = str(self.repo.active_branch.name)
            return True
        except Exception as e:
            raise e

    def get_branches(self):
        lte = self.repo.branches
        return [str(branch.name) for branch in lte]

    def get_current_branch(self):
        return self.branch

    def get_all_commits(self):
        return list(self.repo.iter_commits(self.branch))

    def set_branch(self, branch):
        if branch in self.get_branches():
            self.branch = branch
            return True
        else:
            return False

    def get_all_commit_amend(self, hash):
        """
        Get all commits from a hash to HEAD
        :param hash: the hash to start from
        :return: the list of commits
        """
        commits = self.repo.git.log("--pretty=format:%H", f"{hash}..HEAD")
        commits += "\n" + self.repo.git.log("--pretty=format:%H", f"{hash}") # Adding the first because the first commit is not included

        # detect new lines
        commits = commits.splitlines()

        # get commit info for each commit
        commit_info = []
        for commit in self.get_all_commits():
            if commit.hexsha in commits:
                commit_info.append(commit)

        # Order commit info with the order of commits array
        commit_info_ordered = []
        for commit in commits:
            for info in commit_info:
                if commit == info.hexsha:
                    commit_info_ordered.append(info)

        return commit_info_ordered

    def backup_project(self):
        """
        Backup the project to a zip file in a backup folder in the folder containing the project directory
        """
        print(f"Backup project {self.path} to {self.path}/../backup/")

        # create backup folder if not exist
        if not os.path.exists(f"{self.path}/../backup/"):
            os.mkdir(f"{self.path}/../backup/")
        # create a zip file
        shutil.make_archive(f"{self.path}/../backup/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}", 'zip', self.path)
        print("Backup done")

    def init_amend(self, commit_hash, root=False):
        """
        Init the amend process
        :param commit_hash: the commit hash to start from
        :param root: if true, start from the first commit of the branch and ignore the commit_hash
        """
        # get current git editor
        try:
            git_editor = self.repo.config_reader().get_value("core", "editor")
        except Exception as e:
            git_editor = None  # if no git editor
            pass

        # check if os is windows or linux
        if os.name == "nt":
            self.repo.config_writer().set_value("core", "editor", f"python.exe {config.git_editor_path}").release()
        else:
            self.repo.config_writer().set_value("core", "editor", f"python3 {config.git_editor_path}").release()

        # start rebase with custom editor
        if not root:
            self.repo.git.rebase("-i", commit_hash, _bg=False)
        else:
            # rebase from the first commit of the branch
            self.repo.git.rebase("-i", "--root", _bg=False)

        # reset git editor
        if git_editor is not None:
            self.repo.config_writer().set_value("core", "editor", git_editor).release()
        else:
            self.repo.config_writer().remove_option("core", "editor").release()

    def amend_next(self, author, date, message):
        """
        Amend the next commit
        :param author: the author name
        :param date: the commit date
        :param message: the commit message
        """
        # save author config (name + email)
        name = self.repo.config_reader().get_value("user", "name")
        email = self.repo.config_reader().get_value("user", "email")

        # set author in config (name + email)
        name = author.split("<")[0].strip()
        email = author.split("<")[1].split(">")[0].strip()
        self.repo.config_writer().set_value("user", "name", name).release()
        self.repo.config_writer().set_value("user", "email", email).release()

        self.repo.git.environment().update(GIT_COMMITTER_DATE = date, GIT_AUTHOR_DATE = date)
        self.repo.git.commit("--amend", "--reset-author", "--date", date, "-m", message)
        self.repo.git.rebase("--continue")

        # reset author config (name + email)
        self.repo.config_writer().set_value("user", "name", name).release()
        self.repo.config_writer().set_value("user", "email", email).release()

    def get_first_commit(self):
        """
        :return: the hash of the first commit of the current branch
        """
        return self.repo.git.rev_list("--max-parents=0", "HEAD").splitlines()[0]


def get_timestamp(date_str):
    # convert 2023-04-10 16:22:25+02:00 to a timestamp
    try:
        return int(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S%z").timestamp())
    except ValueError:
        return int(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timestamp())


def get_date(timestamp):
    # convert timestamp to 2023-04-10 16:22:25+02:00
    from datetime import datetime, timedelta, timezone

    d = datetime.now(timezone.utc).astimezone()
    utc_offset = d.utcoffset() // timedelta(seconds=1)

    # convert utcoffset to hour like +02:00 or -05:00
    utc_offset = int(utc_offset / 3600)
    utc_offset = f"{utc_offset:+03d}:00"

    d = datetime.fromtimestamp(timestamp)

    # convert datetime to string
    date_str = d.strftime("%Y-%m-%d %H:%M:%S")
    date_str += utc_offset

    return date_str


