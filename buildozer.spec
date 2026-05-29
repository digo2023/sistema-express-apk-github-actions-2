[app]
title = Sistema Express
package.name = sistemaexpress
package.domain = br.com.expresscolorado
version = 1.0

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,txt,md,db,sqlite,sql,pdf,csv,xlsx,xls,sh
source.exclude_dirs = .git,bin,build,.buildozer,__pycache__,.pytest_cache

requirements = python3,kivy==2.3.0,rich==13.7.1,openpyxl==3.1.5,pypdf==5.1.0,pillow

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 35
android.minapi = 23
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a


[buildozer]
log_level = 2
warn_on_root = 0
