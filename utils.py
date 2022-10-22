import os
import shutil
import re


# TODO: improve upon this with a dedicated visual error section in the GUI
def set_last_err(exception):
    print(exception)


def run_rename(in_dir, in_pattern, out_pattern, settings):
    try:
        in_regex = re.compile(in_pattern)
    except Exception as ex:
        set_last_err(ex)
        return

    def rename(rootpath, filename):
        new_filename = in_regex.sub(out_pattern, filename)
        if filename != new_filename:
            shutil.move(os.path.join(rootpath, filename), os.path.join(rootpath, new_filename))

        return new_filename

    for root, dirs, files in os.walk(in_dir):
        if settings.file_mode in ['files', 'both']:
            for file in files:
                try:
                    if in_regex.fullmatch(file) is None:  # only rename if input pattern matches entire filename
                        continue
                    rename(root, file)
                except Exception as ex:
                    if not settings.skip_errors or type(ex) == re.error:
                        set_last_err(ex)
                        return

        if settings.file_mode in ['folders', 'both']:
            for i in range(len(dirs)):
                try:
                    if in_regex.fullmatch(dirs[i]) is None:  # only rename if input pattern matches entire filename
                        continue
                    dirs[i] = rename(root, dirs[i])
                except Exception as ex:
                    if not settings.skip_errors or type(ex) == re.error:
                        set_last_err(ex)
                        return

        if not settings.recursive:
            break


def run_delete(in_dir, in_pattern, settings):
    try:
        in_regex = re.compile(in_pattern)
    except re.error as ex:
        set_last_err(ex)
        return

    def delete_if_match(rootpath, filename):
        if in_regex.fullmatch(filename) is None:
            return False

        fullpath = os.path.join(rootpath, filename)
        if os.path.isdir(fullpath):
            shutil.rmtree(fullpath, ignore_errors=settings.skip_errors)
        else:
            os.remove(fullpath)
        return True

    for root, dirs, files in os.walk(in_dir):
        if settings.file_mode in ['files', 'both']:
            for file in files:
                try:
                    delete_if_match(root, file)
                except Exception as ex:
                    if not settings.skip_errors or type(ex) == re.error:
                        set_last_err(ex)
                        return

        if settings.file_mode in ['folders', 'both']:
            i = 0
            end_i = len(dirs)
            while i < end_i:
                try:
                    if delete_if_match(root, dirs[i]):
                        del dirs[i]
                        i -= 1
                        end_i -= 1
                except Exception as ex:
                    if not settings.skip_errors or type(ex) == re.error:
                        set_last_err(ex)
                        return

                i += 1

        # run only one iteration of os.walk if recursion is off
        if not settings.recursive:
            break


def run_copy_or_move(in_dir, in_pattern, out_dir, settings, copy=False):
    try:
        in_regex = re.compile(in_pattern)
    except Exception as ex:
        set_last_err(ex)
        return

    for root, dirs, files in os.walk(in_dir):
        if settings.file_mode in ['files', 'both']:
            for file in files:
                try:
                    if copy:
                        copy_func(in_dir, root, out_dir, in_regex, file)
                    else:
                        move_func(in_dir, root, out_dir, in_regex, file)
                except Exception as ex:
                    if not settings.skip_errors or type(ex) == re.error:
                        set_last_err(ex)
                        return

        if settings.file_mode in ['folders', 'both']:
            i = 0
            end_i = len(dirs)
            while i < end_i:
                try:
                    if copy:
                        if copy_func(in_dir, root, out_dir, in_regex, dirs[i]):
                            # folder was copied, don't recurse into it
                            del dirs[i]
                            i -= 1
                            end_i -= 1
                    else:
                        move_func(in_dir, root, out_dir, in_regex, dirs[i])
                except Exception as ex:
                    if not settings.skip_errors or type(ex) == re.error:
                        set_last_err(ex)
                        return

                i += 1

        # run only one iteration of os.walk if recursion is off
        if not settings.recursive:
            break


def copy_func(orig_dir, rootpath, out_dir, pattern, filename):
    if pattern.fullmatch(filename) is None:
        return False

    fullpath = os.path.join(rootpath, filename)
    full_outpath = os.path.join(out_dir, os.path.relpath(os.path.join(rootpath, filename), orig_dir))

    if fullpath != full_outpath:
        if os.path.isdir(fullpath):
            shutil.copytree(fullpath, full_outpath)
        else:
            required_folder = os.path.join(full_outpath, '..')
            if not os.path.exists(required_folder):
                os.makedirs(os.path.normpath(required_folder))
            shutil.copy2(fullpath, full_outpath)
    return True


def move_func(orig_dir, rootpath, out_dir, pattern, filename):
    if pattern.fullmatch(filename) is None:
        return

    fullpath = os.path.join(rootpath, filename)
    full_outpath = os.path.join(out_dir, os.path.relpath(os.path.join(rootpath, filename), orig_dir))

    if fullpath != full_outpath:
        required_folder = os.path.join(full_outpath, '..')
        if not os.path.exists(required_folder):
            os.makedirs(os.path.normpath(required_folder))

        shutil.move(fullpath, full_outpath)
