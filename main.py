from slabinfo_utils import *

SLABINFO_DATA_PATH = 'data_local/slabinfo_2016-6-10_2:20_10:00.data'


def get_slabinfos():
    with open(SLABINFO_DATA_PATH, 'r') as f:
        slabinfos = f.read()
    parsed_slabinfos = [parse_slabinfo(each) for each in slabinfos.split('\n\n')]
    return parsed_slabinfos


def extract_frames_ratio(slabinfos):
    output_path = "aggregations/frames_ratio.csv"
    res = []
    for slab_caches in slabinfos:
        pages_per_slab_type = dict()
        for cache in slab_caches:
            idx = cache.pages_per_slab
            old_value = 0
            if idx in pages_per_slab_type.keys():
                old_value = pages_per_slab_type[idx]
            new_value = old_value + idx * cache.num_slabs
            pages_per_slab_type[idx] = new_value
        res.append(pages_per_slab_type)
    # save into aggregations in .csv
    formatted_res = []
    for each in res:
        newline = '{}\n'.format(','.join([str(each[idx]) for idx in sorted(each)]))
        formatted_res.append(newline)
    print len(formatted_res)
    # save to csv
    with open(output_path, 'w') as f:
        f.writelines(formatted_res)
    print "frames ration extracted"


def main():
    slabinfos = get_slabinfos()
    dump_to_mariadb(slabinfos, "data_20160610_0220_20160610_1000")
    # extract_frames_ratio(slabinfos)


if __name__ == '__main__':
    main()
