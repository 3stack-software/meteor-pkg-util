import json
import os
import re

import click
import pkg_resources
import yaml


@click.command()
@click.argument('package_dir', type=click.Path())
@click.option('--config', type=click.File(), envvar='MPKGUTIL_CONF', default=lambda: pkg_resources.resource_filename(__name__, 'default.yaml'))
@click.option('--landmark', default='//MPKGUTIL')
def cli(package_dir, config, landmark):
    # click.echo('package_dir={0!r}'.format(package_dir))
    # click.echo('config={0!r}'.format(config))
    conf = yaml.load(config)
    # click.echo("conf={0!r}".format(conf))
    # click.echo('landmark={0!r}'.format(landmark))

    write_package_js(package_dir, conf, landmark)


def write_package_js(package_dir, groups, landmark_comment):
    js_statements = "\n\n".join(make_js_statement(mp, m, o) for mp, m, o in get_matching_files(package_dir, groups)) + "\n"
    with open(os.path.join(package_dir, 'package.js'), 'r+b') as fp:
        lines_before, lines_after = read_outside_landmarks(fp.read(), landmark_comment)
        fp.seek(0)
        fp.truncate()
        fp.write(lines_before)
        fp.write(js_statements)
        fp.write(lines_after)


def read_outside_landmarks(text, landmark_comment):
    lines = text.splitlines()
    n_tag = 0
    before = []
    after = []
    for line in lines:
        if n_tag == 0:
            before.append(line)
        if line.lstrip().startswith(landmark_comment):
            n_tag += 1
        if n_tag == 2:
            after.append(line)

        if n_tag > 2:
            raise RuntimeError("Too many {0} landmarks".format(landmark_comment))

    if n_tag != 2:
        raise RuntimeError("{0} x {1} landmarks found (Expected 2)".format(n_tag, landmark_comment))
    return "\n".join(before) + "\n",  "\n".join(after) + "\n"


def get_matching_files(package_dir, groups):
    filenames = list_files(package_dir)
    for group in groups:
        matched_patterns, matched_filenames, filenames = get_all_matching(group['patt'], filenames)
        if matched_filenames:
            if group.get('exclude', False):
                continue
            yield matched_patterns, matched_filenames, group

    if filenames:
        raise RuntimeError("The following files weren't matched: {0!r}".format(filenames))


def get_all_matching(patterns, filenames):
    matched_patterns = []
    matched_files = []
    remainder = filenames
    for pattern in patterns:
        matched, remainder = get_matching(pattern, remainder)
        if matched:
            matched_patterns.append(pattern)
            matched_files += matched
    return matched_patterns, matched_files, remainder


def get_matching(pattern, filenames):
    matched = []
    remainder = []
    for filename in filenames:
        if re.match(pattern + r'\Z(?ms)', filename):
            matched.append(filename)
        else:
            remainder.append(filename)
    return matched, remainder


def pth_cmp(a, b):
    a_path, a_file = os.path.split(a)
    b_path, b_file = os.path.split(b)
    r = cmp(a_path, b_path)
    if r != 0:
        return r
    return cmp(a_file, b_file)


def list_files(folder):
    paths = []
    cwd = os.getcwd()
    try:
        os.chdir(folder)
        for folder, subs, files in os.walk('.'):
            folder = folder[2:] #  Strip off './'
            for file in files:
                full_path = os.path.join(folder, file)
                paths.append(full_path)
        return sorted(paths, cmp=pth_cmp)
    finally:
        os.chdir(cwd)


FMT_REGULAR = """  api.addFiles([
    // {patterns}
    {files}
  ], [{cs}]);"""
FMT_ASSET = """  api.addFiles([
    // {patterns}
    {files}
  ], [{cs}], {{isAsset: true}});"""
FMT_ASSET_V1_2 = """  api.addAssets([
    // {patterns}
    {files}
  ], [{cs}]);"""


def make_js_statement(matched_patterns, matching, group):
    cs = []
    if group.get('client', False):
        cs.append('client')
    if group.get('server', False):
        cs.append('server')
    fmt = FMT_REGULAR
    if group.get('asset', False):
        fmt = FMT_ASSET_V1_2
    return fmt.format(
        patterns="\n    // ".join(matched_patterns),
        files=",\n    ".join(json.dumps(m) for m in matching),
        cs=", ".join(json.dumps(t) for t in cs)
    )
