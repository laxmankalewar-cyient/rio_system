# Cahange odoo iocn to Company icon..
--> need to change favicon.ico to in odoo/addons/web/static/src/img/favicon.ico 
to custome icon with same name.

# Change user Menu bar

Need to Change User Menu inside the odoo/addons/web/static/src/xml/base.xml
<t t-name="UserMenu.Actions">
    <a role="menuitem" href="#" data-menu="documentation" class="dropdown-item">Documentation</a>
    <a role="menuitem" href="#" data-menu="support" class="dropdown-item">Support</a>
    <div role="separator" class="dropdown-divider"/>
    <a role="menuitem" href="#" data-menu="settings" class="dropdown-item">Preferences</a>
    <a role="menuitem" href="#" data-menu="account" class="dropdown-item">My Odoo.com account</a>
    <a role="menuitem" href="#" data-menu="logout" class="dropdown-item">Log out</a>
</t>

#change page titale in javascript 
--> need to change zopenerp to Kts in odoo/addons/web/static/src/webclient/webclient.js
(line number is 36)
