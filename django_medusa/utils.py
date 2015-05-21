from __future__ import print_function
import imp
from django.conf import settings
from importlib import import_module
import sys


def get_static_renderers():
    module_name = 'renderers'
    renderers = []

    modules_to_check = []

    # Hackish: do this in case we have some project top-level
    # (homepage, etc) urls defined project-level instead of app-level.
    settings_module = settings.SETTINGS_MODULE
    if settings_module:
        if "." in settings_module:
            # strip off '.settings" from end of module
            # (want project module, if possible)
            settings_module = settings_module.split(".", 1)[0]
        modules_to_check += [settings_module, ]

    # INSTALLED_APPS that aren't the project itself (also ignoring this
    # django_medusa module)
    try:
        from django.apps import apps
        installed_apps = [app.module.__name__ for app in apps.get_app_configs()]
    except ImportError:  # Fallback for Django < 1.7
        installed_apps = settings.INSTALLED_APPS
    modules_to_check += filter(
        lambda x: (x != "django_medusa") and (x != settings_module),
        installed_apps
    )

    for app in modules_to_check:
        try:
            import_module(app)
            app_path = sys.modules[app].__path__
        except AttributeError:
            print("Skipping app '%s'... (Not found)" % app)
            continue
        try:
            imp.find_module(module_name, app_path)
        except ImportError:
            print("Skipping app '%s'... (No 'renderers.py')" % app)
            continue
        try:
            app_render_module = import_module('%s.%s' % (app, module_name))
            if hasattr(app_render_module, "renderers"):
                renderers += getattr(app_render_module, module_name)
            else:
                print("Skipping app '%s'... ('%s.renderers' does not contain "\
                      "'renderers' var (list of render classes)" % (app, app))
        except AttributeError:
            print("Skipping app '%s'... (Error importing '%s.renderers')" % (
                app, app
            ))
            continue
        print ("Found renderers for '%s'..." % app)
    return tuple(renderers)
