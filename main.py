from slabinfo_utils import *

SLABINFO_PATH = "data_local/slabinfo.txt"   # default: /proc/slabinfo


def get_slabinfo():
    with open(SLABINFO_PATH, 'r') as f:
        slabinfo = f.read()
    return slabinfo


def main():
    slabinfo = get_slabinfo()
    slab_caches = parse_slabinfo(slabinfo)
    pages_per_slab_type = dict()
    for cache in slab_caches:
        idx = cache.pages_per_slab
        old_value = 0
        if idx in pages_per_slab_type.keys():
            old_value = pages_per_slab_type[idx]
        new_value = old_value + idx * cache.num_slabs
        pages_per_slab_type[idx] = new_value
    print pages_per_slab_type


if __name__ == '__main__':
    main()
