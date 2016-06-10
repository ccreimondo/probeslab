
class SlabCache(object):
    """Objected line in /proc/slabinfo."""
    NR_PARTS = 3
    NR_BASIC_PARTS = 6
    NR_TUNABLES_PARTS = 4
    NR_SLABDATA_PARTS = 4
    # attr index in each part
    IDX_NAME = 0
    IDX_ACTIVE_OBJS = 1
    IDX_NUMOBJS = 2
    IDX_OBJSIZE = 3
    IDX_OBJPERSLAB = 4
    IDX_PAGESPERSLAB = 5
    IDX_LIMIT = 1
    IDX_BATCHCOUNT = 2
    IDX_SHAREDFACTOR = 3
    IDX_ACTIVE_SLABS = 1
    IDX_NUMSLABS = 2
    IDX_SHAREDAVAIL = 3

    def __init__(self, slabinfo_line=None):
        # basic
        self.name = None
        self.active_objs = 0
        self.num_objs = 0
        self.obj_size = 0
        self.objs_per_slab = 0
        self.pages_per_slab = 0
        # tunables
        self.limit = 0
        self.batch_count = 0
        self.shared_factor = 0
        # slabdata
        self.active_slabs = 0
        self.num_slabs = 0
        self.shared_avail = 0

        if slabinfo_line is not None:
            self.init(slabinfo_line)

    def init(self, slabinfo_line):
        # e.g. btrfs_delayed_data_ref      0      0    112   36    1 :
        #  tunables    0    0    0 : slabdata      0      0      0
        parts = slabinfo_line.split(':')
        if len(parts) != self.NR_PARTS:
            raise Exception(
                "Problems parsing slabinfo line: {}".format(slabinfo_line))
        # parse basic parts
        basic_parts = parts[0].strip(' ').split()
        if len(basic_parts) != self.NR_BASIC_PARTS:
            raise Exception(
                "Problems parsing basic part in slabinfo line: {}".format(basic_parts))
        self.name = basic_parts[self.IDX_NAME]
        self.active_objs = int(basic_parts[self.IDX_ACTIVE_OBJS])
        self.num_objs = int(basic_parts[self.IDX_NUMOBJS])
        self.obj_size = int(basic_parts[self.IDX_OBJSIZE])
        self.objs_per_slab = int(basic_parts[self.IDX_OBJPERSLAB])
        self.pages_per_slab = int(basic_parts[self.IDX_PAGESPERSLAB])
        # parse tunables parts
        tunables_parts = parts[1].strip(' ').split()
        if len(tunables_parts) != self.NR_TUNABLES_PARTS:
            raise Exception(
                "Problems parsing tunables part in slabinfo line".format(tunables_parts))
        self.limit = int(tunables_parts[self.IDX_LIMIT])
        self.batch_count = int(tunables_parts[self.IDX_BATCHCOUNT])
        self.shared_factor = int(tunables_parts[self.IDX_SHAREDFACTOR])
        # parse slabdata parts
        slabdata_parts = parts[2].strip(' ').split()
        if len(slabdata_parts) != self.NR_SLABDATA_PARTS:
            raise Exception(
                "Problems parsing slabdata part in slabinfo line".format(slabdata_parts))
        self.active_slabs = int(slabdata_parts[self.IDX_ACTIVE_SLABS])
        self.num_slabs = int(slabdata_parts[self.IDX_NUMSLABS])
        self.shared_factor = int(slabdata_parts[self.IDX_SHAREDAVAIL])

    def in_dict(self):
        return self.__dict__

    def in_tuple(self):
        return (self.name, self.active_objs, self.num_objs,
                self.objs_per_slab, self.pages_per_slab,
                self.limit, self.batch_count, self.shared_factor,
                self.active_slabs, self.num_slabs, self.shared_avail,)


def parse_slabinfo(slabinfo):
    lines = slabinfo.split('\n')
    slab_caches = []
    # exceptions may be raised in 'lines[1:0]' or SlabCache construct stage
    for slabinfo_line in lines[2:]:
        if slabinfo_line == '':
            continue
        slab_caches.append(SlabCache(slabinfo_line))
    return slab_caches


"""
CREATE DATABASE slabinfos;
CREATE USER 'slab'@'localhost' IDENTIFIED BY 'slab';
GRANT ALL ON slabinfos.* TO 'slab'@'localhost';
FLUSH PRIVILEGES;
"""


TABLE_TEMPLATE = """
CREATE TABLE IF NOT EXISTS `{}` (
  `timestamp` INT NOT NULL,
  `name` VARCHAR(50) NOT NULL,
  `active_objs` INT NOT NULL,
  `num_objs` INT NOT NULL,
  `objs_per_slab` INT NOT NULL,
  `pages_per_slab` INT NOT NULL,
  `limit` INT NOT NULL,
  `batch_count` INT NOT NULL,
  `shared_factor` INT NOT NULL,
  `active_slabs` INT NOT NULL,
  `num_slabs` INT NOT NULL,
  `shared_avail` INT NOT NULL,
  PRIMARY KEY (`timestamp`, `name`)
)
"""

SQL_INSERT_TEMPLATE = """
INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def dump_to_mariadb(slabinfos, table_name):
    import mysql.connector as mariadb
    conn = mariadb.connect(user='slab', password='slab', database='slabinfos')
    # create table
    cursor = conn.cursor()
    cursor.execute(TABLE_TEMPLATE.format(table_name))
    # insert data
    values = []
    for idx, slab_caches in enumerate(slabinfos):
        for cache in slab_caches:
            values.append((idx,) + cache.in_tuple())
    cursor.executemany(SQL_INSERT_TEMPLATE.format(table_name), values)
    conn.commit()
    conn.close()


def test():
    slabinfo_lines = ["btrfs_delayed_data_ref      0      0    112   36    1 : "
                      "tunables    0    0    0 : slabdata      0      0      0",
                      "btrfs_extent_buffer      0      0    280   29    2 : "
                      "tunables    0    0    0 : slabdata      0      0      0",]
    slabinfos = [[SlabCache(each) for each in slabinfo_lines]]
    dump_to_mariadb(slabinfos, "test")


if __name__ == '__main__':
    test()
