#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2009-2012:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.
### Will be populated by the UI with it's own value
app = None

import time

from shinken.util import safe_print

# Get plugin's parameters from configuration file
params = {}

def load_cfg():
    global params

    import os,sys
    from config_parser import config_parser
    from shinken.log import logger
    plugin_name = os.path.splitext(os.path.basename(__file__))[0]
    try:
        currentdir = os.path.dirname(os.path.realpath(__file__))
        configuration_file = "%s/%s" % (currentdir, 'plugin.cfg')
        logger.debug("Plugin configuration file: %s" % (configuration_file))
        scp = config_parser('#', '=')
        params = scp.parse_config(configuration_file)

        logger.debug("WebUI plugin '%s', configuration loaded." % (plugin_name))
        return True
    except Exception, exp:
        logger.warning("WebUI plugin '%s', configuration file (%s) not available: %s" % (plugin_name, configuration_file, str(exp)))
        return False

def checkauth():
    user = app.get_user_auth()

    if not user:
        app.bottle.redirect("/user/login")
    else:
        return user

def reload_cfg():
    load_cfg()
    app.bottle.redirect("/config")


# Contact page
def show_contact(name):
    user = checkauth()

    if not user.is_admin and user.get_name != name:
      app.bottle.redirect('/contacts')

    return {
        'app': app, 'user': user, 'params': params,
        'contact': app.datamgr.get_contact(name)
        }

# All contacts
def show_contacts():
    user = checkauth()

    if user.is_admin:
        contacts = app.datamgr.get_contacts()
    else:
        contacts = (user,)

    return {
        'app': app, 'user': user, 'params': params,
        'contacts': sorted(app.datamgr.get_contacts(), key=lambda contact: contact.contact_name)
        }

# Load plugin configuration parameters
load_cfg()

pages = {
        reload_cfg: {'routes': ['/reload/contacts']},

        show_contact: {'routes': ['/contact/:name'], 'view': 'contact', 'static': True},
        show_contacts: {'routes': ['/contacts'], 'view': 'contacts', 'static': True},
        }