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

def kde_conf(project):    
    image_dir = project.image_dir()
        
    os.system("chroot %s chown -R pisi:wheel /home/pisi/.config" % image_dir)
    os.system("mkdir -p %s/home/pisi/Desktop" % image_dir)
    os.system("chroot %s chown -R pisi:wheel /home/pisi/.local" % image_dir)
   

    #etc
    os.system("cp -rf ./data/etc/skel/.config %s/home/pisi" % image_dir)
    os.system("cp -rf ./data/etc/skel/.config/ %s/etc/skel/" % image_dir)
    
    os.system("cp -rf ./data/etc/skel/ %s/etc/" % image_dir)
    os.system("cp -f ./data/etc/99-live-tz-fix %s/etc/NetworkManager/dispatcher.d/" % image_dir)
    
    
    os.system("chroot %s chmod -R 777 /home/pisi/.config" % image_dir)
    os.system("cp -rf ./data/etc/profile.d/ %s/etc/" % image_dir)
    os.system("cp -rf ./data/etc/xdg/ %s/etc/" % image_dir)
   
    os.system("cp -f ./data/desktop_conf/kde_conf/script/* %s/usr/local/bin" % image_dir)

   
    os.system("cp -f ./data/desktop_conf/kde_conf/kde_menu/*.desktop %s/usr/share/applications/" % image_dir)
    os.system("cp -f ./data/desktop_conf/kde_conf/kde_menu/*.directory %s/usr/share/desktop-directories/" % image_dir)
   
    os.system("cp -rf ./data/desktop_conf/kde_conf/usr %s/" % image_dir)
    os.system("cp -rf ./data/desktop_conf/kde_conf/wallpapers %s/usr/share" % image_dir)


    os.system("chmod +x %s/usr/local/bin/*" % image_dir)


    ##iptal edilenler
    # os.system("mkdir -p %s/home/pisi/Masaüstü" % image_dir)
    # os.system("cp -rf ./data/desktop_conf/kde_conf/wallpapers %s/usr/share" % image_dir)
    #os.system("cp -rf ./data/desktop_conf/kde_conf/.local %s/home/pisi" % image_dir)
    #os.system("cp -rf ./data/desktop_conf/kde_conf/usr/share/look-and-feel/maia-light %s/usr/share/look-and-feel/" % image_dir)
    #os.system("cp -rf ./data/desktop_conf/kde_conf/xdg/ %s/etc/" % image_dir)
    #os.system("mkdir -p %s/home/pisi/.config" % image_dir)
    

    if "yali" in project.all_install_image_packages:
        shutil.copy("./data/installer/yali/yali.desktop", "%s/home/pisi/Desktop/" % image_dir )
        # shutil.copy("./data/yali/yali.desktop", "%s/home/pisi/Masaüstü/" % image_dir)
        shutil.copy("./data/installer/yali/yali-rescue.desktop", "%s/home/pisi/Desktop/" % image_dir)        
        # shutil.copy("./data/yali/yali-rescue.desktop", "%s/home/pisi/Masaüstü/" % image_dir)
    
    if "yali-rs" in project.all_install_image_packages:
        shutil.copy("./data/installer/yali-rs/yali.desktop", "%s/home/pisi/Desktop/" % image_dir )
       
    # 31-08-2025 eklendi
    os.system("cp -rf ./data/etc/skel/ {}/etc/".format(image_dir))
    os.system("cp -rf ./data/etc/ {}/".format(image_dir))
    #os.system("cp -rf ./data/desktop_conf/kde_conf/kde_menu/ {}/usr/share/applications/".format(image_dir))
    

def xfce_conf(image_dir):
    image_dir = project.image_dir()
    if "xfce4-panel" in project.all_install_image_packages:
        run("mkdir -p {}/home/pisi/Desktop".format(image_dir))

        shutil.copy("./data/installer/yali/yali.desktop", "{}/home/pisi/Desktop/".format(image_dir))
        shutil.copy("./data/installer/yali/yali-rescue.desktop", "{}/home/pisi/Desktop/".format(image_dir)) 
        
        #shutil.copy("./data/xfce4/yali-desktop-copy.sh", "{}/usr/bin/".format(image_dir))
        #shutil.copy("./data/xfce4/etc/xdg/autostart/yali-desktop.desktop", "{}/etc/xdg/autostart/".format(image_dir))
        
        shutil.copy("./data/xfce4/usr/share/backgrounds/xfce/pisiBackground.jpg", "{}/usr/share/backgrounds/xfce/".format(image_dir))
        shutil.copy("./data/xfce4/etc/lightdm/web-greeter.yml", "{}/etc/lightdm/".format(image_dir))
        os.system("cp -rf ./data/xfce4/etc/skel/.config/ {}/home/pisi/".format(image_dir))
        os.system("cp -rf ./data/xfce4/etc/skel/.config/ {}/etc/skel/".format(image_dir))
        #os.system("cp -rf ./data/xfce4/etc/lightdm/ {}/etc/".format(image_dir))

        os.system("cp -rf ./data/xfce4/usr/share/ {}/usr/".format(image_dir))

def etc_conf(image_dir):
    os.system("cp -rf ./data/etc/skel/ {}/etc/".format(image_dir))
    os.system("cp -rf ./data/etc/ {}/".format(image_dir))
   
def calamares_conf(project):
    image_dir = project.image_dir()
    if "Calamares" in project.all_install_image_packages:
        os.system("cp -rf ./data/installer/calamares/branding {}/usr/share/calamares/".format(image_dir))
        os.system("cp -rf ./data/installer/calamares/usr {}/".format(image_dir))
        
        shutil.copy("./data/installer/calamares/settings.conf", "{}/usr/share/calamares/".format(image_dir))
        shutil.copy("{}/usr/share/applications/calamares.desktop".format(image_dir), "{}/home/pisi/Desktop/".format(image_dir))

def grub_conf(project):
    image_dir = project.image_dir()
    if "grub2" in project.all_install_image_packages:
        print("Copying grub2 themes...")
        os.system('cp -rf ./data/grub/ {}/usr/share/'.format(image_dir))
        

def yali_conf(project):

    image_dir = project.image_dir()
    if "yali" in project.all_install_image_packages:
        shutil.copy("./data/installer/yali/yali.desktop", "{}/usr/share/applications/".format(image_dir))
        shutil.copy("./data/installer/yali/org.pisilinux.yali.policy", "{}/usr/share/polkit-1/actions/".format(image_dir))
        shutil.copy("./data/installer/yali/yali-rescue.desktop", "{}/usr/share/applications/".format(image_dir))

def sddm_conf(project):
    image_dir = project.image_dir()
    if "sddm" in project.all_install_image_packages:
        shutil.copy("./data/sddm/theme.conf", "{}/usr/share/sddm/themes/pisilinux/".format(image_dir))
        shutil.copy("./data/sddm/bg.jpg", "{}/usr/share/sddm/themes/pisilinux/".format(image_dir))
        