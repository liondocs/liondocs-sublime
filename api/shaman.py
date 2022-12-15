import os
import subprocess


class Shaman(object):
    """
    It is in charge of obtaining the SHA of the received file. If the repo_path
    parameter is passed, the SHA of the same file is obtained but in the
    content repository.
    """

    def __init__(self, target_path, repo_path):
        super(Shaman, self).__init__()
        self.target_path = target_path
        self.repo_path = repo_path

    def __build_meta(self, sha):
        """
        Convert given SHA in metadata format
        """
        base = "l10n:\n\tsourceCommit: {0}".format(sha)
        return base

    def get_file_sha(self, returnas='raw'):
        """
        Obtiene el SHA
        """
        rel_path = self.target_path.relative_to(self.repo_path)
        # May freeze sublime text gui due to subprocess
        # implement threading?

        # Change current working dir
        os.chdir(str(self.repo_path))

        command = "git log -1 --pretty=%H " + str(rel_path)
        last_commit = subprocess.check_output(command, shell=True)
        last_commit = last_commit.decode().strip()

        if returnas == 'raw':
            # Return just raw SHA
            return last_commit
        elif returnas == 'meta':
            # Return SHA in metadata format
            return self.__build_meta(last_commit)
