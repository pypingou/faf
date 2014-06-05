# Copyright (C) 2014  ABRT Team
# Copyright (C) 2014  Red Hat, Inc.
#
# This file is part of faf.
#
# faf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# faf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with faf.  If not, see <http://www.gnu.org/licenses/>.

from pyfaf.actions import Action
from pyfaf.common import FafError
from pyfaf.opsys import systems
from pyfaf.queries import (get_associate_by_name,
                           get_opsys_by_name,
                           get_releases)
from pyfaf.storage import (AssociatePeople,
                           OpSysReleaseComponentAssociate)


class PullAssociates(Action):
    name = "pull-associates"

    def __init__(self):
        super(PullAssociates, self).__init__()

    def run(self, cmdline, db):
        if len(cmdline.opsys) == 0:
            tasks = []
            for opsys in systems.values():
                releases = get_releases(db, opsys_name=opsys.nice_name)
                tasks += [(opsys, release) for release in releases]
        elif len(cmdline.opsys) == 1:
            shortname = cmdline.opsys[0]
            if shortname not in systems:
                self.log_error("Operating system '{0}' is not installed"
                               .format(shortname))
                return 1

            opsys = systems[shortname]
            db_opsys = get_opsys_by_name(db, opsys.nice_name)
            if db_opsys is None:
                self.log_error("Operating system '{0}' is not initialized"
                               .format(shortname))
                return 1

            if len(cmdline.opsys_release) < 1:
                tasks = [(opsys, r) for r in db_opsys.releases]
            else:
                tasks = [(opsys, r) for r in db_opsys.releases
                         if r.version in cmdline.opsys_release]
        else:
            tasks = []
            for shortname in cmdline.opsys:
                if shortname not in systems:
                    self.log_warn("Operating system '{0}' is not installed"
                                  .format(shortname))
                    continue

                opsys = systems[shortname]
                db_opsys = get_opsys_by_name(db, opsys.nice_name)
                if db_opsys is None:
                    self.log_warn("Operating system '{0}' is not initialized"
                                  .format(shortname))
                    continue

                tasks += [(opsys, rel) for rel in db_opsys.releases]

        new_associates = {}
        i = 0
        for opsys, db_release in tasks:
            i += 1

            self.log_info("[{0} / {1}] Processing {2} {3}"
                          .format(i, len(tasks), opsys.nice_name,
                                  db_release.version))

            j = 0
            for db_component in db_release.components:
                j += 1

                name = db_component.component.name
                self.log_debug("  [{0} / {1}] Processing component '{2}'"
                               .format(j, len(db_release.components), name))

                acls = opsys.get_component_acls(name,
                                                release=db_release.version)
                k = 0
                for associate in acls:
                    k += 1
                    self.log_debug("    [{0} / {1}] Processing associate '{2}'"
                                   .format(k, len(acls), associate))

                    db_associate = get_associate_by_name(db, associate)
                    if db_associate is None:
                        if associate in new_associates:
                            db_associate = new_associates[associate]
                        else:
                            db_associate = AssociatePeople()
                            db_associate.name = associate
                            db.session.add(db_associate)
                            new_associates[associate] = db_associate

                            self.log_info("Adding a new associate '{0}'"
                                          .format(associate))

                    associates = [a.associates for a in db_component.associates]
                    if db_associate not in associates:
                        db_associate_comp = OpSysReleaseComponentAssociate()
                        db_associate_comp.component = db_component
                        db_associate_comp.associates = db_associate
                        db.session.add(db_associate_comp)

                        self.log_info("Assigning associate '{0}' to component "
                                      "'{1}'".format(associate, name))

                db.session.flush()

    def tweak_cmdline_parser(self, parser):
        parser.add_opsys(multiple=True)
        parser.add_opsys_release(multiple=True)
