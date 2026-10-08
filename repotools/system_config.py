#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import shutil

def grub_conf(project):
    image_dir = project.image_dir()
    os.system("cp -rf ./data/grub/ %s/usr/share/grub/" % image_dir)
    
    os.system("cp -rf ./data/grub2/icons/ {}/usr/share/grub/themes/pisilinux/".format(image_dir))
    