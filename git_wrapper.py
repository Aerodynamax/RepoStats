import os
from git import Commit, Actor, Repo

import git.types

from gitdb.db.loose import LooseObjectDB
from git.db import GitCmdObjectDB

from typing import Iterator



class GitActor(Actor):

    commits: int = 0

    def __init__(
            self,
            name: str | None,
            email: str | None,
            commits: int = 0
        ) -> None:

        super().__init__(
            name=name,
            email=email
        )

        self.commits = commits

    @staticmethod
    def from_actor(actor: Actor, commits: int = 0):
        return GitActor(
            name=actor.name,
            email=actor.email,
            commits=commits
        )



class GitRepo(Repo):

    name: str
    commits: list[Commit] = []
    authors: set[GitActor]

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
        
        _authors = set( commit.author for commit in self.commits.copy() )

        self.authors = set(map(lambda author: GitActor.from_actor(actor=author, commits=[commit.author for commit in self.commits].count(author)), list(_authors)))
