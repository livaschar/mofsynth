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

from . cli import _transaction_summary, _return_cli_parser
from . utils import main

if __name__ == '__main__':

    args = _return_cli_parser().parse_args()
    _transaction_summary(args)

    inp = input('\nIs this ok[y/N]: ')
    print('\n')

    if inp.upper() == 'Y':
        main(
            args.directory,
            args.function,
            args.supercell_limit
            )
    else:
        print('Operation aborted.')