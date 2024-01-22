# This file is part of MOF-Synth.
# Copyright (C) 2023 Charalampos G. Livas

# MOF-Synth is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# python - m MOFSynth [function] [directory]

import sys
import os

# Add the directory containing your package to the sys.path
package_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(package_directory)

from __cli__ import _return_cli_parser, _transaction_summary
from __utils__ import run


if __name__ == '__main__':

    args = _return_cli_parser().parse_args()
    
    _transaction_summary(args)

    inp = input('\nIs this ok [y/n]: ')
    print('\n')

    if inp.lower() == 'y':
        run(args.directory)
    else:
        print('Operation aborted.\n')