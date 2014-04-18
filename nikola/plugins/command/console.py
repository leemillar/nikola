# -*- coding: utf-8 -*-

# Copyright © 2012-2014 Chris Warrick, Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function, unicode_literals

import os

from nikola import __version__, Nikola
from nikola.plugin_categories import Command
from nikola.utils import get_logger, STDERR_HANDLER, req_missing

LOGGER = get_logger('console', STDERR_HANDLER)


class CommandConsole(Command):
    """Start debugging console."""
    name = "console"
    shells = ['ipython', 'bpython', 'plain']
    doc_purpose = "start an interactive Python console with access to your site"
    doc_description = """\
The site engine is accessible as `SITE`, and the config as `conf`.
If no option (-b, -i, -p), it tries -i, then -b, then -p."""
    header = "Nikola v" + __version__ + " -- {0} Console (conf = configuration, SITE = site engine, commands = nikola commands)"
    cmd_options = [
        {
            'name': 'bpython',
            'short': 'b',
            'long': 'bpython',
            'type': bool,
            'default': False,
            'help': 'Use bpython',
        },
        {
            'name': 'ipython',
            'short': 'i',
            'long': 'plain',
            'type': bool,
            'default': False,
            'help': 'Use IPython',
        },
        {
            'name': 'plain',
            'short': 'p',
            'long': 'plain',
            'type': bool,
            'default': False,
            'help': 'Use the plain Python interpreter',
        },
    ]

    def ipython(self, willful=True):
        """IPython shell."""
        try:
            import IPython
        except ImportError as e:
            if willful:
                req_missing(['IPython'], 'use the IPython console')
            raise e  # That’s how _execute knows whether to try something else.
        else:
            SITE = self.site  # NOQA
            config = self.site.config  # NOQA
            commands = self.context['commands']  # NOQA
            IPython.embed(header=self.header.format('IPython'))

    def bpython(self, willful=True):
        """bpython shell."""
        try:
            import bpython
        except ImportError as e:
            if willful:
                req_missing(['bpython'], 'use the bpython console')
            raise e  # That’s how _execute knows whether to try something else.
        else:
            bpython.embed(banner=self.header.format('bpython'), locals_=self.context)

    def plain(self, willful=True):
        """Plain Python shell."""
        import code
        try:
            import readline
        except ImportError:
            pass
        else:
            import rlcompleter
            readline.set_completer(rlcompleter.Completer(self.context).complete)
            readline.parse_and_bind("tab:complete")

        pythonrc = os.environ.get("PYTHONSTARTUP")
        if pythonrc and os.path.isfile(pythonrc):
            try:
                execfile(pythonrc)  # NOQA
            except NameError:
                pass

        code.interact(local=self.context, banner=self.header.format('Python'))

    def _execute(self, options, args):
        """Start the console."""
        self.site.scan_posts()
        # Create nice object with all commands:
        commands = Commands()
        for cmd in self.site.plugin_manager.getPluginsOfCategory('Command'):
            commands.__dict__[cmd.name] = cmd.plugin_object

        self.context = {
            'conf': self.site.config,
            'SITE': self.site,
            'Nikola': Nikola,
            'commands': commands,
        }
        if options['bpython']:
            self.bpython(True)
        elif options['ipython']:
            self.ipython(True)
        elif options['plain']:
            self.plain(True)
        else:
            for shell in self.shells:
                try:
                    return getattr(self, shell)(False)
                except ImportError:
                    pass
            raise ImportError


class Commands(object):
    pass
