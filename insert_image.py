import sublime
import sublime_plugin
import os
import sys
import hashlib
import platform
import re
import subprocess
import shutil
# from imp import reload

import subprocess
import json

def get_python_sitepackages():

    cmd = 'python3 -c "import site; print(site.getsitepackages())"'
    s = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    out = s.stdout.read().decode("utf-8")
    s.stdout.close()

    result = json.loads(out.replace("'", '"'))

    cmd = 'python3 -m site --user-site'
    s = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    out = s.stdout.read().decode("utf-8")
    s.stdout.close()

    result.append(out.strip())

    return result

site_packages = get_python_sitepackages()
for site_package in site_packages:
    if not site_package in sys.path:
        sys.path.append(site_package)

# print(sys.path)
from qiniu import Auth, put_file


class MarkdownInsertImageCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        super(MarkdownInsertImageCommand, self).__init__(view)
        self.settings = sublime.load_settings('MarkdownInsertImage.sublime-settings')

        self.use_local_path= self.settings.get('use_local_path', False)
        self.local_path= self.settings.get('local_path', 'assets')
        self.isQiniu= self.settings.get('isQiniu', True)
        self.qiniuAK= self.settings.get('qiniuAK', "")
        self.qiniuSK= self.settings.get('qiniuSK', "")
        self.qiniuBucket= self.settings.get('qiniuBucket', '')
        self.qiniuDomain= self.settings.get('qiniuDomain', '')


        # print(self.qiniuDomain)
    
    def upload_qiniu(self, input_path):

        access_key = self.qiniuAK
        secret_key = self.qiniuSK
        bucket_name = self.qiniuBucket

        qiniu_auth = Auth(access_key, secret_key)

        filename = os.path.basename(input_path)
        key = filename
        token = qiniu_auth.upload_token(bucket_name, key)
        ret, info = put_file(token, key, input_path, check_crc=True)

        print("upload ret:{}".format(ret))

        if ret and ret['key'] == key:
            return "http://{}/{}".format(self.qiniuDomain, filename)
        else:
            return ''

    def paste(self, mdFile, image_path):
        projectDir = sublime.active_window().folders()[0]

        filename = os.path.basename(mdFile)
        basename = os.path.splitext(os.path.basename(mdFile))[0]

        assetsPath = os.path.join(projectDir , self.local_path)

        if not os.path.exists(assetsPath):
            os.mkdir(assetsPath)


        md5 = hashlib.md5()

        with open(image_path, 'rb') as f:
            md5.update(f.read())
            f.close()

        hash = md5.hexdigest()[0:8]

        filename = "" + basename.replace('/\.\w+$/', '').replace('/\s+/g', '').split('-')[0] + "-" +  hash

        isGIF = False;

        if not isGIF:
            filename += ".png";
        else:
            filename += ".gif";

        print(filename)


        filepath = os.path.join(assetsPath, filename)

        if image_path != filepath:
            shutil.copy2(image_path, filepath)

        return self.upload_qiniu(filepath)




    def run(self, edit):

        get_python_sitepackages()

        view = self.view

        if self.isQiniu:
            if self.qiniuAK == ''  or self.qiniuSK == '' or self.qiniuBucket == '' or self.qiniuDomain == '':
                sublime.active_window().status_message("Qiniu upload enabled, but qiniu settings not valid")
                return

        mdFile = view.file_name()
        # mdFile = src_filepath
        # print(mdFile)
        if not mdFile:
            sublime.active_window().status_message("Current file not saved, save first.")
            return

        # self.view.insert(edit, 0, "Hello, World!")

        clipboard = sublime.get_clipboard()

        # print(type(clipboard))

        # print(clipboard)

        filelist = []

        # print(type(clipboard))

        if type(clipboard) == str and len(clipboard) > 0:

            # print(clipboard)

            # print(clipboard.startswith("x-special/nautilus-clipboard"))

            if clipboard.startswith("x-special/nautilus-clipboard"):

                files = clipboard.splitlines()

                if len(files) == 3 and files[2].startswith("file:///"):

                    filepath = filefiles[2][7:]

                    if  os.path.exists(filepath):
                        filelist.append(filepath)


            if clipboard.startswith("/"):

                files = clipboard.splitlines()

                for file in files:
                    if(file.startswith("/")) and os.path.exists(file):
                        filelist.append(file)



        print(filelist)

        extensions = re.compile("(gif|jpg|jpeg|png)$", re.I)
        for file in filelist:
            if extensions.search(file):
                # print("{}-{}".format(mdFile, file))
                url = self.paste(mdFile, file)

                for pos in view.sel():
                    # print("scope name: %r" % (view.scope_name(pos.begin())))
                    if 'text.html.markdown' in view.scope_name(pos.begin()):
                        view.insert(edit, pos.begin(), "![](%s)\n" % url)
                    else:
                        view.insert(edit, pos.begin(), "%s" % url)

