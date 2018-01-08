#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Update Me !

This module has been written in order to be the main entry for every tests in a
directory which contain a list to test.

Also consider this script a clean script which have to be filled for every repository.

Author:
    @Funilrys, Nissar Chababy <contactTAfunilrysTODcom>

Contributors:
    Let's contribute !

    @GitHubUsername, Name, Email (optional)
"""

from json import decoder, dump, loads
from os import sep as directory_separator
from os import chmod, environ, getcwd, path, stat
from re import compile as comp
from re import sub as substrings
from re import escape
from shutil import copyfileobj
from stat import S_IEXEC
from subprocess import PIPE, Popen
from time import strftime

from requests import get


class Settings(object):  # pylint: disable=too-few-public-methods
    """
    This class will save all data that can be called from anywhere in the code.
    """

    # This variable will help us keep a track on info.json content.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    informations = {}

    # This variable should be initiated with the raw link to the hosts file or the
    # list we are going to test.
    #
    # Note: The variable name should not be changed.
    # Note: This variable is auto updated by Initiate()
    #
    # Example: "https://raw.githubusercontent.com/AdAway/adaway.github.io/master/hosts.txt"
    raw_link = ''

    # This variable should be initiated with the name of the list once downloaded.
    # Recommended formats:
    #  - GitHub Repository:
    #    - GitHubUsername@RepoName.list
    #  - GitHub organization:
    #    - GitHubOrganisationName@RepoName.list
    #  - Others:
    #    - websiteDomainName.com@listName.list
    #
    # Note: The variable name should not be changed.
    # Note: This variable is auto updated by Initiate()
    #
    # Example: "adaway.github.io@AdAway.list"
    list_name = ''

    # This variable will help us know where we are working into the filesystem.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    current_directory = getcwd() + directory_separator

    # This variable will help us know which file we are going to test.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    file_to_test = current_directory

    # This variable will help us know what how many days we have to wait until next test.
    #
    # Note: This variable is auto updated by Initiate()
    days_until_next_test = 0

    # This variable will help us know the date of the last test.
    #
    # Note: This variable is auto updated by Initiate()
    last_test = 0

    # This variable will help us manage the implementation of days_until_next_test and last_test.
    #
    # Note: This variable is auto updated by Initiate()
    currently_under_test = False

    # This variable will help us know where should the info.json file be located.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    repository_info = current_directory + 'info.json'

    # This variable will help us know which version of PyFunceble we are going to use.
    #
    # Note: True = master | False = dev
    # Note: This variable is auto updated by Initiate()
    stable = False

    # This variable represent the PyFunceble infrastructure.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    PyFunceble = {
        'PyFunceble.py': 'https://raw.githubusercontent.com/funilrys/PyFunceble/master/PyFunceble.py',  # pylint: disable=line-too-long
        'tool.py': 'https://raw.githubusercontent.com/funilrys/PyFunceble/master/tool.py'}

    # This variable is used to match [ci skip] from the git log.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    regex_travis = '[ci skip]'

    # This variable is used to set the number of minutes before we stop the script under Travis CI.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    autosave_minutes = 10

    # This variable is used to set the default commit message when we commit
    # under Travic CI.

    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    commit_autosave_message = ''

    # This variable is used to set permanent_license_link.

    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    permanent_license_link = 'https://raw.githubusercontent.com/dead-hosts/repository-structure/master/LICENSE'  # pylint: disable=line-too-long


class Initiate(object):
    """
    Initiate several actions.
    """

    def __init__(self):  # pylint: disable=too-many-branches
        self.travis()
        self.travis_permissions()
        self.settings()

    @classmethod
    def travis(cls):
        """
        Initiate Travis CI settings.
        """

        Helpers.Command('git remote rm origin', False).execute()
        Helpers.Command(
            "git remote add origin https://" +
            "%s@github.com/%s.git" %
            (environ['GH_TOKEN'],
             environ['TRAVIS_REPO_SLUG']),
            False).execute()
        Helpers.Command(
            'git config --global user.email "%s"' %
            (environ['GIT_EMAIL']), False).execute()
        Helpers.Command(
            'git config --global user.name "%s"' %
            (environ['GIT_NAME']), False).execute()
        Helpers.Command(
            'git config --global push.default simple').execute()
        Helpers.Command('git checkout master', True).execute()

        return

    def settings(self):
        """
        Read info.json and retranscript its data into the script.
        """

        if path.isfile(Settings.repository_info):
            content = Helpers.File(Settings.repository_info).read()
            Settings.informations = Helpers.Dict().from_json(content)

            for index in Settings.informations:
                if Settings.informations[index] != '':
                    if index == 'name':
                        continue

                    try:
                        getattr(Settings, index)
                        if index in [
                                'stable',
                                'currently_under_test'] and Settings.informations[index].isdigit():
                            setattr(Settings, index, bool(
                                int(Settings.informations[index])))
                        elif index in ['days_until_next_test', 'last_test', 'autosave_minutes'] \
                                and Settings.informations[index].isdigit():
                            setattr(
                                Settings, index, int(
                                    Settings.informations[index]))
                        else:
                            setattr(
                                Settings, index, Settings.informations[index])
                    except AttributeError:
                        raise Exception(
                            '"%s" into %s in unknown.' %
                            (index, Settings.repository_info))
                else:
                    raise Exception(
                        'Please complete "%s" into %s' %
                        (index, Settings.repository_info))

            for file in Settings.PyFunceble:
                file_path = Settings.current_directory + file

                if not path.isfile(file_path) or Settings.stable:
                    download_link = Settings.PyFunceble[file].replace(
                        'master', 'dev')
                else:
                    download_link = Settings.PyFunceble[file].replace(
                        'dev', 'master')

                Helpers.Download(download_link, file_path).link()

                self.travis_permissions()

                stats = stat(file_path)
                chmod(file_path, stats.st_mode | S_IEXEC)

            Settings.file_to_test += Settings.list_name

            regex_new_test = r'Launch\stest'

            if not path.isfile(
                    Settings.file_to_test) or Helpers.Regex(
                        Helpers.Command(
                            'git log -1',
                            False).execute(),
                        Settings.regex_travis,
                        return_data=False,
                        escape=True).match() or Helpers.Regex(
                            Helpers.Command(
                                'git log -1',
                                False).execute(),
                            regex_new_test,
                            return_data=False,
                            escape=True).match():

                self.list_file()
                if path.isdir(Settings.current_directory + 'output'):
                    Helpers.Command(
                        Settings.current_directory +
                        'tool.py -c',
                        False).execute()

    @classmethod
    def travis_permissions(cls):
        """
        Set permissions in order to avoid issues before commiting.
        """

        build_dir = environ['TRAVIS_BUILD_DIR']
        commands = [
            'sudo chown -R travis:travis %s' % (build_dir),
            'sudo chgrp -R travis %s' % (build_dir),
            'sudo chmod -R g+rwX %s' % (build_dir),
            'sudo chmod 777 -Rf %s.git' % (build_dir + directory_separator),
            r"sudo find %s -type d -exec chmod g+x '{}' \;" % (build_dir)
        ]

        for command in commands:
            Helpers.Command(command, False).execute()

        if Helpers.Command('git config core.sharedRepository').execute() == '':
            Helpers.Command(
                'git config core.sharedRepository group',
                False).execute()

        return

    def list_file(self):
        """
        Download Settings.raw_link.
        """

        if Helpers.Download(Settings.raw_link, Settings.file_to_test).link():
            Helpers.Command(
                'dos2unix ' +
                Settings.file_to_test,
                False).execute()

            self.travis_permissions()
            return True
        raise Exception(
            'Unable to download the the file. Please check the link.')

    def PyFunceble(self):  # pylint: disable=invalid-name
        """
        Install and run PyFunceble.
        """

        tool_path = Settings.current_directory + 'tool.py'
        # pylint: disable=invalid-name
        PyFunceble_path = Settings.current_directory + \
            'PyFunceble.py'

        command_to_execute = 'sudo python3 %s --dev -u && ' % (tool_path)
        command_to_execute += 'sudo python3 %s -v && ' % (tool_path)
        command_to_execute += 'export TRAVIS_BUILD_DIR=%s && ' % environ['TRAVIS_BUILD_DIR']
        command_to_execute += 'sudo python3 %s --dev --autosave-minutes %s --commit-autosave-message "[Autosave] %s" --commit-results-message "[Results] %s" -i && ' % (  # pylint: disable=line-too-long
            tool_path, Settings.autosave_minutes, Settings.commit_autosave_message, Settings.commit_autosave_message)  # pylint: disable=line-too-long
        command_to_execute += 'sudo python3 %s -v && ' % (PyFunceble_path)
        command_to_execute += 'sudo python3 %s --travis -a -ex --plain --split -t 2 -f %s ' % (
            PyFunceble_path, Settings.file_to_test)

        if Settings.days_until_next_test >= 1 and Settings.last_test != 0:
            retest_date = Settings.last_test + \
                (24 * Settings.days_until_next_test * 3600)
        else:
            retest_date = int(strftime('%s')) - 60

        if not Helpers.Regex(
                Helpers.Command(
                    'git log -1',
                    False).execute(),
                Settings.regex_travis,
                return_data=False,
                escape=True).match() or not path.isfile(
                    Settings.current_directory +
                    'output' +
                    directory_separator +
                    'continue.json') or int(
                        strftime('%s')) >= retest_date:

            self.travis_permissions()

            print(Helpers.Command(command_to_execute).execute())
            Settings.informations['last_test'] = strftime('%s')
            Helpers.Dict(
                Settings.informations).to_json(
                    Settings.repository_info)

            Helpers.Download(
                Settings.permanent_license_link,
                Settings.current_directory +
                'LICENSE').link()

            self.travis_permissions()


class Helpers(object):  # pylint: disable=too-few-public-methods
    """
    Well thanks to those helpers I wrote :)
    """

    class Dict(object):
        """
        Dictionary manipulations.

        Arguments:
            main_dictionnary: A dict, the main_dictionnary to pass to the whole class.
        """

        def __init__(self, main_dictionnary=None):

            if main_dictionnary is None:
                self.main_dictionnary = {}
            else:
                self.main_dictionnary = main_dictionnary

        def to_json(self, destination):
            """
            Save a dictionnary into a JSON file.

            Arguments:
                destination: A string, A path to a file where we're going to Write
                    the converted dict into a JSON format.
            """

            with open(destination, 'w') as file:
                dump(
                    self.main_dictionnary,
                    file,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True)

        @classmethod
        def from_json(cls, data):
            """
            Convert a JSON formated string into a dictionary.

            Arguments:
                data: A string, a JSON formeted string to convert to dict format.
            """

            try:
                return loads(data)
            except decoder.JSONDecodeError:
                return {}

    class File(object):  # pylint: disable=too-few-public-methods
        """
        File treatment/manipulations.

        Arguments:
            file: A string, a path to the file to manipulate.
        """

        def __init__(self, file):
            self.file = file

        def read(self):
            """
            Read a given file path and return its content.
            """

            with open(self.file, 'r', encoding="utf-8") as file:
                funilrys = file.read()

            return funilrys

    class Download(object):  # pylint: disable=too-few-public-methods
        """
        This class will initiate a download of the desired link.

        Arguments:
            link_to_download: A string, the link to the file we are going to download.
            destination: A string, the destination of the downloaded data.
        """

        def __init__(self, link_to_download, destination):
            self.link_to_download = link_to_download
            self.destination = destination

        def link(self):
            """
            This method initiate the download.
            """

            request = get(self.link_to_download, stream=True)

            if request.status_code == 200:
                with open(self.destination, 'wb') as file:
                    request.raw.decode_content = True
                    copyfileobj(request.raw, file)

                del request

                return True
            return False

    class Command(object):
        """
        Shell command execution.

        Arguments:
            command: A string, the command to execute.
            allow_stdout: A bool, If true stdout is always printed otherwise stdout
                is passed to PIPE.
        """

        def __init__(self, command, allow_stdout=True):
            self.decode_type = 'utf-8'
            self.command = command
            self.stdout = allow_stdout

        def decode_output(self, to_decode):
            """Decode the output of a shell command in order to be readable.

            Arguments:
                to_decode: byte(s), Output of a command to decode.
            """
            if to_decode is not None:
                return to_decode.decode(self.decode_type)
            return False

        def execute(self):
            """Execute the given command."""

            if not self.stdout:
                process = Popen(
                    self.command,
                    stdout=PIPE,
                    stderr=PIPE,
                    shell=True)
            else:
                process = Popen(self.command, stderr=PIPE, shell=True)

            (output, error) = process.communicate()

            if process.returncode != 0:
                decoded = self.decode_output(error)

                if not decoded:
                    return 'Unkown error. for %s' % (self.command)

                print(decoded)
                print(Helpers.Command('pwd').execute())
                print(
                    Helpers.Command(
                        'ls -al %s' %
                        environ['TRAVIS_BUILD_DIR']).execute())
                exit(1)
            return self.decode_output(output)

    class Regex(object):  # pylint: disable=too-few-public-methods

        """A simple implementation ot the python.re package


        :param data: A string, the data to regex check
        :param regex: A string, the regex to match
        :param return_data: A boolean, if True, return the matched string
        :param group: A integer, the group to return
        :param rematch: A boolean, if True, return the matched groups into a
            formated list. (implementation of Bash ${BASH_REMATCH})
        :param replace_with: A string, the value to replace the matched regex with.
        :param occurences: A int, the number of occurence to replace.
        """

        def __init__(self, data, regex, **args):
            # We initiate the needed variable in order to be usable all over
            # class
            self.data = data

            # We assign the default value of our optional arguments
            optional_arguments = {
                "escape": False,
                "group": 0,
                "occurences": 0,
                "rematch": False,
                "replace_with": None,
                "return_data": True
            }

            # We initiate our optional_arguments in order to be usable all over the
            # class
            for (arg, default) in optional_arguments.items():
                setattr(self, arg, args.get(arg, default))

            if self.escape:  # pylint: disable=no-member
                self.regex = escape(regex)
            else:
                self.regex = regex

        def match(self):
            """Used to get exploitable result of re.search"""

            # We initate this variable which gonna contain the returned data
            result = []

            # We compile the regex string
            to_match = comp(self.regex)

            # In case we have to use the implementation of ${BASH_REMATCH} we use
            # re.findall otherwise, we use re.search
            if self.rematch:  # pylint: disable=no-member
                pre_result = to_match.findall(self.data)
            else:
                pre_result = to_match.search(self.data)

            if self.return_data and pre_result is not None:  # pylint: disable=no-member
                if self.rematch:  # pylint: disable=no-member
                    for data in pre_result:
                        if isinstance(data, tuple):
                            result.extend(list(data))
                        else:
                            result.append(data)

                    if self.group != 0:  # pylint: disable=no-member
                        return result[self.group]  # pylint: disable=no-member
                else:
                    result = pre_result.group(
                        self.group).strip()  # pylint: disable=no-member

                return result
            elif not self.return_data and pre_result is not None:  # pylint: disable=no-member
                return True
            return False

        def replace(self):
            """Used to replace a matched string with another."""

            if self.replace_with is not None:  # pylint: disable=no-member
                return substrings(
                    self.regex,
                    self.replace_with,  # pylint: disable=no-member
                    self.data,
                    self.occurences)  # pylint: disable=no-member
            return self.data


Initiate().PyFunceble()
