MarkdownInsertImage
==============================================================
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/lizhiyong2000/MarkdownInsertImage/master/LICENSE)

This [MarkdownInsertImage](https://packagecontrol.io/browse) package is a SublimteText 3 plugin, which helps you insert images easily, especially when editing a markdown file, save the image into file and upload the image to qiniu cloud.

## Installation
This plugin can be installed with [PackageControl](https://packagecontrol.io/packages/MardownInsertImage).

Also you can manualy download the source codes from [Github](https://github.com/lizhiyong2000/MarkdownInsertImage) and install locally.

### Dependcies
####  1. [SideBarEnhancements](https://packagecontrol.io/packages/SideBarEnhancements)

Use SideBarEnhancements we can insert multi images at a time.
####  2. Python packages
Some python packages are needed:
```
pip3 install qiniu
```

## How to use

### 1. Settings

Open MarkdownInsertImage settings by menu path:`Preferences -> Package Settings -> MarkdownInsertImage -> Settings - User`, and input your `qiniuAK` ,`qiniuSK` ,`qiniuBucket` and `qiniuDomain`.

![](http://carforeasy.cn/README-1ebdc431.png)

### 2. Copy from sidbar
First copy images' path from sidbar, then  insert images from clipboard into markdown file using `ctrl+alt+v`.

![](http://carforeasy.cn/README-298f5405.gif)


### 3. Copy from Files 

First copy image from File Manager, then  insert images from clipboard into markdown file using `ctrl+alt+v`.

![](http://carforeasy.cn/README-d8118598.gif)










