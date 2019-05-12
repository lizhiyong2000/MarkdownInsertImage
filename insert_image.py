import sublime
import sublime_plugin
import os
import sys
import re
import subprocess
import shutil
from imp import reload

print(sys.getdefaultencoding())
reload(sys)
# sys.setdefaultencoding('utf-8')


import os
import sys
from qiniu import Auth, put_file
if 3 != len(sys.argv):
    print('[Usage] %s [dir_set] [filepath]' % os.path.basename(sys.argv[0]))
    sys.exit(0)
else:
    # dir_set 的格式为 image/upload-qiniu/ ，注意末尾带反斜杠/
    dir_set = sys.argv[1]
    file_path = sys.argv[2]
# 个人中心->密匙管理->AK
access_key = '你的AccessKey'
# 个人中心->密匙管理->SK
secret_key = '你的SecretKey'
# 七牛空间名
bucket_name = '你的存储空间名'
qiniu_auth = Auth(access_key, secret_key)
def upload_qiniu(input_path):
    #upload single file to qiniu
    filename = os.path.basename(input_path)
    key = '%s%s' % (dir_set, filename)
    token = qiniu_auth.upload_token(bucket_name, key)
    ret, info = put_file(token, key, input_path, check_crc=True)
    if ret and ret['key'] == key:
        print('%s done' % ('http://www.sylan215.com/' + dir_set + filename))
    else:
        print('%s error' % ('http://www.sylan215.com/' + dir_set + filename))

class ImagePasteCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwgs):
        self.settings = sublime.load_settings('imagepaste.sublime-settings')

        # get the image save dirname
        self.image_dir_name = self.settings.get('image_dir_name', None)
        if len(self.image_dir_name) == 0:
            self.image_dir_name = None
        print("[%d] get image_dir_name: %r"%(id(self.image_dir_name), self.image_dir_name))

    def run_command(self, cmd):
        cwd = os.path.dirname(self.view.file_name())
        print("cmd %r" % cmd)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=os.environ)

        try:
            outs, errs = proc.communicate(timeout=15)
            print("outs %r %r" % (outs, proc))
        except Exception:
            proc.kill()
            outs, errs = proc.communicate()
        print("outs %r, errs %r" % (b'\n'.join(outs.split(b'\r\n')), errs))
        if errs is None or len(errs) == 0:
            return outs.decode()

    def get_filename(self):
        view = self.view
        filename = view.file_name()

        # create dir in current path with the name of current filename
        dirname, _ = os.path.splitext(filename)

        # create new image file under currentdir/filename_without_ext/filename_without_ext%d.png
        fn_without_ext = os.path.basename(dirname)
        if self.image_dir_name is not None:
            subdir_name = os.path.join(os.path.split(dirname)[0], self.image_dir_name)
        else:
            subdir_name = dirname
        if not os.path.lexists(subdir_name):
            os.mkdir(subdir_name)
        i = 0
        while True:
            # relative file path
            rel_filename = os.path.join("%s/%s%d.png" % (self.image_dir_name if self.image_dir_name else fn_without_ext, fn_without_ext, i))
            # absolute file path
            abs_filename = os.path.join(subdir_name, "%s%d.png" % (fn_without_ext, i))
            if not os.path.exists(abs_filename):
                break
            i += 1

        print("save file: " + abs_filename + "\nrel " + rel_filename)
        return abs_filename, rel_filename



    def run(self, edit):
        view = self.view
        print("[%d] image_dir_name: %r"%(id(self.image_dir_name),self.image_dir_name))
        rel_fn = self.paste()

        if not rel_fn:
            view.run_command("paste")
            return
        for pos in view.sel():
            # print("scope name: %r" % (view.scope_name(pos.begin())))
            if 'text.html.markdown' in view.scope_name(pos.begin()):
                view.insert(edit, pos.begin(), "![](%s)" % rel_fn)
            else:
                view.insert(edit, pos.begin(), "%s" % rel_fn)
            # only the first cursor add the path
            break


    def paste(self):
        if sys.platform != 'win32':
            dirname = os.path.dirname(__file__)
            command = ['/usr/bin/python3', os.path.join(dirname, 'bin/imageutil.py'), 'save']
            abs_fn, rel_fn = self.get_filename()
            command.append(abs_fn)

            out = self.run_command(" ".join(command))
            if out and out[:4] == "save":
                return rel_fn
        # else: # win32
        #     ImageFile.LOAD_TRUNCATED_IMAGES = True
        #     im = ImageGrab.grabclipboard()
        #     if im:
        #         abs_fn, rel_fn = self.get_filename()
        #         im.save(abs_fn,'PNG')
        #         return rel_fn

        print('clipboard buffer is not image!')
        return None



