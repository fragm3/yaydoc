import os
import argparse


def _title(value):
    return value.replace('_', ' ').title()


def get_include(dirpath, filename):
    ext = os.path.splitext(filename)[1]
    if ext == '.md':
        directive = 'mdinclude'
    else:
        directive = 'include'
    template = '.. {directive}:: {document}'
    path = os.path.relpath(os.path.join(dirpath, filename))
    document = path.replace(os.path.sep, '/')
    return template.format(directive=directive, document=document)


def get_toctree(dirpath, filenames, caption=''):
    toctree = ['.. toctree::', '   :maxdepth: 1']
    caption_template = '   :caption: {caption}'
    content_template = '   {document}'
    if not caption:
        caption = _title(os.path.basename(dirpath))
        if caption == os.curdir:
            caption = 'Contents'
    toctree.append(caption_template.format(caption=caption))
    # Inserting a blank line
    toctree.append('')

    valid = False
    for filename in filenames:
        path, ext = os.path.splitext(os.path.join(dirpath, filename))
        if ext not in ('.md', '.rst'):
            continue
        document = path.replace(os.path.sep, '/')
        document = document.lstrip('./').rstrip('/')
        toctree.append(content_template.format(document=document))
        valid = True

    if valid:
        return '\n'.join(toctree)
    else:
        return ''


# Any files ignored will not be included in a toctree
def _ignore_files(dirpath, filenames, ignored_filenames, path=None):
    if path is None or os.path.samefile(dirpath, path):
        for filename in ignored_filenames:
            if filename in filenames:
                filenames.remove(filename)



# Any directories ignored will not be walked through to find source files
def _ignore_dirs(dirpath, dirnames, ignored_dirnames, path=None):
    if path is None or os.path.samefile(dirpath, path):
        for dirname in ignored_dirnames:
            if dirname in dirnames:
                dirnames.remove(dirname)


def get_index(root, subprojects, sub_docpaths, javadoc):
    index = []

    subproject_dirs = [subproject.split(os.path.sep)[0]
                       for subproject in subprojects]

    # Include README from root
    root_files = next(os.walk(root))[2]
    if 'README.rst' in root_files:
        index.append(get_include(root, 'README.rst'))
    elif 'README.md' in root_files:
        index.append(get_include(root, 'README.md'))

    # Add toctrees as per the directory structure
    for (dirpath, dirnames, filenames) in os.walk(os.curdir):
        _ignore_files(dirpath, filenames, ['README.rst', 'README.md'], root)
        _ignore_dirs(dirpath, dirnames, ['yaydoctemp', 'yaydocclone', '.git'])
        _ignore_dirs(dirpath, dirnames, ['source'] + subproject_dirs, os.curdir)

        if filenames:
            toctree = get_toctree(dirpath, filenames)
            if toctree:
                index.append(toctree)

    for subproject, sub_docpath in zip(subprojects, sub_docpaths):
        sub_index_path = os.path.normpath(os.path.join(subproject, sub_docpath,
                                                       'index.rst'))
        toctree = get_toctree(os.curdir, [sub_index_path],
                              _title(subproject.split(os.path.sep)[0]))
        index.append(toctree)
    # add javadoc if javadoc exist
    if javadoc != "":
        index = add_javadoc(index)

    return '\n\n'.join(index) + '\n'

def add_javadoc(index):
    javadoc = ["API Documentation", "\n", "=================", "\n",
     "* `javadoc <./javadoc>`_"]
    return index + javadoc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help='Path to the root of the Repository')
    parser.add_argument('-s', '--subprojects', default='',
                        help='Comma seperated subprojects')
    parser.add_argument('-j', '--javadoc', default='',
                        help='Path of java source files for Javadoc')
    parser.add_argument('-d', '--sub-docpaths', default='',
                        help='Comma seperated docpaths for subprojects')
    args = parser.parse_args()
    subprojects, sub_docpaths = [], []
    javadoc = args.javadoc
    if args.subprojects:
        subprojects = [name.strip().replace('/', os.path.sep)
                       for name in args.subprojects.split(',')]
    if args.sub_docpaths:
        sub_docpaths = [name.strip().replace('/', os.path.sep)
                        for name in args.sub_docpaths.split(',')]
    if len(subprojects) != len(sub_docpaths):
        raise ValueError("Invalid arguments")
    content = get_index(args.root, subprojects, sub_docpaths, javadoc)
    with open('index.rst', 'w') as file:
        file.write(content)


if __name__ == '__main__':
    main()
