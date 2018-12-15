
######################################################################
# Helper functions for working directly with filesystem commands
######################################################################

import logging
log = logging.getLogger(__name__)


import os, platform, shutil
from datetime import datetime


def join_path(path1, path2):
    path = os.path.join(path1, path2)
    if path[-1:] == '/':
        path = path[:-1]
    return path


def get_file_extension(path):
    _, extension = os.path.splitext(path)
    return extension


def isdir(path, prefix_blacklist=None):
    if not os.path.isdir(path):
        return False
    if prefix_blacklist is not None:
        for prefix in prefix_blacklist:
            if get_basename(path).startswith(prefix):
                return False
    return True


def isfile(path, allowed_extensions=None):
    if allowed_extensions is not None:
        _, extension = os.path.splitext(path)
        extensions = [ext.lower() for ext in allowed_extensions]
        if extension.lower() not in extensions:
            return False
    return os.path.isfile(path)


def get_basename(path):
    return os.path.basename(path)


def get_path_sep():
    return os.path.sep


def get_path_split(path):
    return os.path.split(path)


def move(src_path, dest_path):
    try:
        shutil.move(src_path, dest_path)
    except IOError:
        log.error("Move file failed: src_path=%s, dest_path=%s" % (src_path, dest_path))
        return False
    return True


def walklevel(some_dir, level=1000):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def trash(src_path, trash_path):

    # check src_path exists
    if not os.path.exists(src_path):
        raise IOError("Source path does not exist")

    # check dest path exists: create if it doesn't
    if not isdir(trash_path):
        # TODO: add try/except
        os.makedirs(trash_path)

    history_filename = '_history.csv'
    history_path = os.path.join(trash_path, history_filename)

    # open history file for writing
    history = open(history_path, 'a')

    # make dest path
    if isfile(src_path):
        filename = get_basename(src_path)
        dest_path = os.path.join(trash_path, filename)
        i = 1
        while isfile(dest_path):
            name, extension = os.path.splitext(filename)
            temp_filename = '%s-%s%s' % (name, i, extension)
            dest_path = os.path.join(trash_path, temp_filename)
            i += 1
    else:
        # src_path is folder
        i = 1
        while isdir(trash_path):
            dest_path = '%s-$s' % (trash_path, i)
            i += 1

    # move file
    if not move(src_path, dest_path):
        return False

    # store in history file
    history.write('%s, %s, %s\n' % (datetime.now(), src_path, dest_path))
    history.close()

    return True


def restore(src_path, trash_path):

    # check trash_path exists
    if not isdir(trash_path):
        log.error("Trash path does not exist (%s)" % trash_path)
        return False

    history_filename = '_history.csv'
    history_path = os.path.join(trash_path, history_filename)

    if not isfile(history_path):
        log.error("History file path does not exist (%s)" % history_path)
        return False

    # open history file for reading
    try:
        history = open(history_path, 'r')
    except IOError():
        log.error("Cannot open history file for reading (%s)" % history_path)
        return False

    history_lines = history.readlines()
    history.close()

    # open history file for writing
    try:
        history = open(history_path, 'w')
    except IOError():
        log.error("Cannot open history file for writing (%s)" % history_path)
        return False

    # get history lines with matching src_paths
    matching_lines = []
    for line in history_lines:
        try:
            if line.split(', ')[1] == src_path:
                matching_lines.append(line)
        except IndexError:
            log.error("History file contains a bad line '%s'" % line)
            continue

    try:
        last_matching_line = matching_lines[-1]
    except IndexError:
        log.error("History file contains no matches for target file'%s'" % src_path)
        return False

    # get path of target file in the trash folder, including removing the carriage return [:-1]
    trashed_file_path = last_matching_line.split(', ')[2][:-1]

    # move file
    if not move(src_path=trashed_file_path, dest_path=src_path):
        return False

    # re-write the history file without the last_matching_line
    for line in history_lines:
        if line != last_matching_line:
            history.write(line)
    history.close()

    return True


def get_creation_date(path):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        created = os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            created = stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            created = stat.st_mtime
    return str(datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M:%S"))


def get_creation_year(path):
    creation_date = datetime.strptime(get_creation_date(path), "%Y-%m-%d %H:%M:%S")
    return creation_date.year


def get_folders(path, prefix_blacklist = None, include_subfolders=False):

    response = []

    level = 0
    if include_subfolders:
        level = 1000

    for root, dirs, files in walklevel(path, level=level):
        for name in dirs:
            folder_path = os.path.join(root, name)
            if isdir(folder_path, prefix_blacklist=prefix_blacklist):
                response.append(folder_path)
            if prefix_blacklist is not None:
                tempdirs = []
                for dir in dirs:
                    blacklisted = False
                    for prefix in prefix_blacklist:
                        if dir.startswith(prefix):
                            log.info('Blacklisted folder: %s' % os.path.join(root, dir))
                            blacklisted = True
                    if not blacklisted:
                        tempdirs.append(dir)
                dirs[:] = tempdirs
    return response


def get_files(path, extensions=None, folder_prefix_blacklist=None, include_subfolders=False):

    response = []

    level = 0
    if include_subfolders:
        level = 1000

    for root, dirs, files in walklevel(path, level=level):
        for name in files:
            file_path = os.path.join(root, name)
            if isfile(file_path, extensions):
                response.append(file_path)
        if folder_prefix_blacklist is not None:
            tempdirs = []
            for dir in dirs:
                blacklisted = False
                for prefix in folder_prefix_blacklist:
                    if dir.startswith(prefix):
                        log.info('Blacklisted folder: %s' % os.path.join(root, dir))
                        blacklisted = True
                if not blacklisted:
                    tempdirs.append(dir)
            dirs[:] = tempdirs
    return response

##################################################################
# tests
##################################################################

if __name__ == "__main__":

    print get_creation_year('/Users/Home/Pictures/ORIGINALS/Google Photos Backup/photo_backup_test2.jpg')
