import os
from git import Commit, Actor, Repo

import git.types

from gitdb.db.loose import LooseObjectDB
from git.db import GitCmdObjectDB

from typing import Iterator


class GitRepo(Repo):

    name: str
    commits: list[Commit]
    authors: set[Actor]

    def __init__(
            self,
            path: git.types.PathLike | None = None,
            odbt: type[LooseObjectDB] = GitCmdObjectDB,
            search_parent_directories: bool = False,
            expand_vars: bool = True
        ) -> None:

        super().__init__(
            path=path,
            odbt=odbt, 
            search_parent_directories=search_parent_directories, 
            expand_vars=expand_vars
        )

        # obtain info once for reuse
        self.name = os.path.basename(self.working_dir)

        self.commits = list(self.iter_commits("--all"))
        
        self.authors = set( commit.author for commit in self.commits )
