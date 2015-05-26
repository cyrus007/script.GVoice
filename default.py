#
#  XBMC Gtalk Notification Addon
#
#  Copyright (C) 2012 swapan@yahoo.com
#  http://github.com/cyrus007/script.GVoice
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

# Script constants
__addon__       = "Gtalk Addon"
__addon_id__    = "script.GVoice"
__author__      = "cyrus007 <swapan@yahoo.com>"
__url__         = "http://github.com/cyrus007/xbmc-addons/script.GVoice"
__version__     = "0.0.1"

# Modules
import sys, os
import xbmc, xbmcaddon, xbmcgui, xbmcvfs
import re, traceback

xbmc.log("[%s]: Version %s initialized.\n" % (__addon__,__version__))

# Get environment OS
__os__          = os.environ.get( "OS", "win32" )
xbmc.log("[%s]: XBMC for %s\n" % (__addon__,__os__))

__language__    = xbmcaddon.Addon(__addon_id__).getLocalizedString
RESOURCE_PATH   = os.path.join(xbmcaddon.Addon(__addon_id__).getAddonInfo('path'), "resources" )

sys.path.append(os.path.join(RESOURCE_PATH,'lib'))
import xmpp


#############################################################################################################
def log(msg):
    try:
        xbmc.log("[%s]: %s\n" % (__addon__,str(msg)))
    except:
        pass

#############################################################################################################
def processCall(client, message):
        global gtalk_notification_timeout
        global DEBUG
        log(">> processCall ")
        text = str(message.getBody())
        user = str(message.getFrom().getStripped())
        if (DEBUG == "true"):
            log(">> User: " + user)
            log(">> Message " + text)
        xbmc_notification_string = unicode(text)
#       xbmc_notification_img = xbmc.translatePath(os.path.join(RESOURCE_PATH,'media','xbmc-xmpppy.png'))
        log(">> Notification: " + xbmc_notification_string)
        xbmc.executebuiltin("XBMC.Notification("+ __language__(30050) +","+ xbmc_notification_string +","+ str(gtalk_notification_timeout*1000) +")")
    

#################################################################################################################
# Starts here
#################################################################################################################
#if (__name__ == '__main__'):
try:
    log("PATH: "+ xbmcaddon.Addon(__addon_id__).getAddonInfo('path'))
    settings = xbmcaddon.Addon(__addon_id__)
    first_run = settings.getSetting("first_run")
    if (first_run == "true" or first_run == ''):
        settings.openSettings()
        settings.setSetting("first_run","false")
    DEBUG = settings.getSetting("gtalk_debug")
    chatbot = settings.getSetting("gtalk_chatbot")
    if (chatbot == "true"):
        log(">> Background service is disabled.")
        del settings
    else:

        gtalk_host = settings.getSetting("gtalk_host")
#       gtalk_port = int(settings.getSetting("gtalk_port"))
        gtalk_user = settings.getSetting("gtalk_user")
        gtalk_pass = settings.getSetting("gtalk_pass")
        arr_timeout = [5,10,15,20,25,30]
        gtalk_notification_timeout = int(arr_timeout[int(settings.getSetting("gtalk_notification_timeout"))])
        del settings

        jid = xmpp.JID(gtalk_user)
#       client = xmpp.Client(jid.getDomain(), debug=[])
        client = xmpp.Client(jid.getDomain())
        conn = client.connect()
        if not conn:
            log(">> Unable to connect to server %s"%gtalk_host)
            sys.exit(1)
        if conn <> 'tls':
            log(">> Warning: unable to estabilish secure connection - TLS failed! conn=%s"%conn)

        auth = client.auth(jid.getNode(), gtalk_pass, 'XBMC')
        if not auth:
            log(">> Unable to authorize on %s - check login/password."%gtalk_host)
            sys.exit(1)
        if auth <> 'sasl':
            log(">> Warning: unable to perform SASL auth on %s. Old authentication method used!"%gtalk_host)

        client.RegisterHandler('message', processCall)
        log(">> registered handler 'processCall'.")
        client.sendInitPresence()
        log(">> sent presence notification.")
        while (not xbmc.abortRequested):
            client.Process(1)
        client.disconnect()
except:
    xbmc_notification_string = unicode(str(sys.exc_info()[1]))
    xbmc_notification_img = xbmc.translatePath(os.path.join(RESOURCE_PATH,'media','xbmc-xmpppy.png'))
    log(">> EXIT Notification: " + xbmc_notification_string)
    xbmc.executebuiltin("XBMC.Notification("+ __language__(30051) +","+ xbmc_notification_string +","+ str(15*1000) +","+ xbmc_notification_img +")")

try:
    sys.modules.clear()
except:
    pass

