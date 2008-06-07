#! /usr/bin/env python
# encoding: utf-8

import os
import Params
import commands
from Configure import g_maxlen
#g_maxlen = 40

VERSION='1.9.0'
APPNAME='jack'
JACK_API_VERSION = '0.1.0'

# these variables are mandatory ('/' are converted automatically)
srcdir = '.'
blddir = 'build'

def display_msg(msg, status = None, color = None):
    sr = msg
    global g_maxlen
    g_maxlen = max(g_maxlen, len(msg))
    if status:
        print "%s :" % msg.ljust(g_maxlen),
        Params.pprint(color, status)
    else:
        print "%s" % msg.ljust(g_maxlen)

def display_feature(msg, build):
    if build:
        display_msg(msg, "yes", 'GREEN')
    else:
        display_msg(msg, "no", 'YELLOW')

def fetch_svn_revision(path):
    cmd = "LANG= "
    cmd += "svnversion "
    cmd += path
    return commands.getoutput(cmd)

def set_options(opt):
    # options provided by the modules
    opt.tool_options('compiler_cxx')
    opt.tool_options('compiler_cc')

    opt.add_option('--dbus', action='store_true', default=False, help='Enable D-Bus JACK (jackdbus)')
    opt.sub_options('linux/dbus')

def configure(conf):
    conf.check_tool('compiler_cxx')
    conf.check_tool('compiler_cc')

    conf.sub_config('linux')
    if Params.g_options.dbus:
        conf.sub_config('linux/dbus')
    conf.sub_config('example-clients')

    conf.env['LIB_PTHREAD'] = ['pthread']
    conf.env['LIB_DL'] = ['dl']
    conf.env['LIB_RT'] = ['rt']
    conf.env['JACK_API_VERSION'] = JACK_API_VERSION

    conf.define('ADDON_DIR', os.path.normpath(conf.env['PREFIX'] + '/lib/jack'))
    conf.define('JACK_LOCATION', os.path.normpath(conf.env['PREFIX'] + '/bin'))
    conf.define('SOCKET_RPC_FIFO_SEMA', 1)
    conf.define('__SMP__', 1)
    conf.define('USE_POSIX_SHM', 1)
    conf.define('JACK_SVNREVISION', fetch_svn_revision('.'))
    conf.define('JACKMP', 1)
    if conf.env['BUILD_JACKDBUS'] == True:
        conf.define('JACK_DBUS', 1)
    conf.write_config_header('config.h')

    display_msg("\n==================")
    display_msg("JACK %s %s" % (VERSION, conf.get_define('JACK_SVNREVISION')))
    print
    display_msg("Install prefix", conf.env['PREFIX'], 'CYAN')
    display_msg("Drivers directory", conf.env['ADDON_DIR'], 'CYAN')
    display_feature('Build with ALSA support', conf.env['BUILD_DRIVER_ALSA'] == True)
    display_feature('Build with FireWire (FreeBob) support', conf.env['BUILD_DRIVER_FREEBOB'] == True)
    display_feature('Build with FireWire (FFADO) support', conf.env['BUILD_DRIVER_FFADO'] == True)
    display_feature('Build D-Bus JACK (jackdbus)', conf.env['BUILD_JACKDBUS'] == True)
    if conf.env['BUILD_JACKDBUS'] == True:
        display_msg('D-Bus service install directory', conf.env['DBUS_SERVICES_DIR'], 'CYAN')
        #display_msg('Settings persistence', xxx)

        if conf.env['DBUS_SERVICES_DIR'] != conf.env['DBUS-1_SESSION_BUS_SERVICES_DIR'][0]:
            print
            print Params.g_colors['RED'] + "WARNING: D-Bus session services directory as reported by pkg-config is"
            print Params.g_colors['RED'] + "WARNING:",
            print Params.g_colors['CYAN'] + conf.env['DBUS-1_SESSION_BUS_SERVICES_DIR'][0]
            print Params.g_colors['RED'] + 'WARNING: but service file will be installed in'
            print Params.g_colors['RED'] + "WARNING:",
            print Params.g_colors['CYAN'] + conf.env['DBUS_SERVICES_DIR']
            print Params.g_colors['RED'] + 'WARNING: You may need to adjust your D-Bus configuration after installing jackdbus'
            print 'WARNING: You can override dbus service install directory'
            print 'WARNING: with --enable-pkg-config-dbus-service-dir option to this script'
            print Params.g_colors['NORMAL'],
    print

def build(bld):
    # process subfolders from here
    bld.add_subdirs('common')
    bld.add_subdirs('linux')
    if bld.env()['BUILD_JACKDBUS'] == True:
        bld.add_subdirs('linux/dbus')
    bld.add_subdirs('example-clients')
    bld.add_subdirs('tests')