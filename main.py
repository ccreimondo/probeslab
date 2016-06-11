from slabinfo_utils import *

SLABINFO_DATA_PATH = 'data_local/slabinfo_2016-6-10_2:20_10:00.data'


def get_slabinfos():
    with open(SLABINFO_DATA_PATH, 'r') as f:
        slabinfos = f.read()
    parsed_slabinfos = [parse_slabinfo(each) for each in slabinfos.split('\n\n')]
    return parsed_slabinfos


def frames_ratio_handler(slabinfo):
    pages_per_slab_type = dict()
    for cache in slabinfo:
        idx = cache.pages_per_slab
        old_value = 0
        if idx in pages_per_slab_type.keys():
            old_value = pages_per_slab_type[idx]
        new_value = old_value + idx * cache.num_slabs
        pages_per_slab_type[idx] = new_value
    return pages_per_slab_type


def extract_frames_ratio(slabinfos):
    output_path = "aggregations/frames_ratio.csv"
    res = map(frames_ratio_handler, slabinfos)
    # save into aggregations in .csv
    formatted_res = []
    for each in res:
        newline = '{}\n'.format(','.join([str(each[idx]) for idx in sorted(each)]))
        formatted_res.append(newline)
    print len(formatted_res)
    # save to csv
    with open(output_path, 'w') as f:
        f.writelines(formatted_res)
    print "frames ratio extracted"


def aoi_steep_handler(slabinfo):
    cache_per_slab_type = dict()
    for cache in slabinfo:
        idx = cache.pages_per_slab
        if idx not in cache_per_slab_type.keys():
            cache_per_slab_type[idx] = []
        cache_per_slab_type[idx].append((cache.name, cache.num_slabs))
    return cache_per_slab_type


def aoi_steep(slabinfos):
    output_path = "aggregations/cache_ratio.csv"
    aoi_idx = [550, 650, 9800, 9920, 12120, 12164, 17970, 18014]
    filtered = [(idx, slabinfos[idx]) for idx in aoi_idx]
    res = [(each[0], aoi_steep_handler(each[1])) for each in filtered]
    # save to file
    formatted_res = []
    # res has been sorted
    for each in res:
        # sort slab type by 1, 2, 4, 8
        in_types = [each[1][idx] for idx in sorted(each[1])]
        for (idx, each_type) in enumerate(in_types):
            formatted_res.append('{},{}\n'.format(each[0], 2**idx))
            # sort caches by num_slabs per slab type
            sorted_caches = sorted(each_type, key=lambda x: x[1], reverse=True)
            for each_cache in sorted_caches:
                if each_cache[1] == 0:
                    continue
                newline = '{},{}\n'.format(each_cache[0], str(each_cache[1]))
                formatted_res.append(newline)
    print len(formatted_res)
    with open(output_path, 'w') as f:
        f.writelines(formatted_res)


def main():
    slabinfos = get_slabinfos()
    # dump_to_mariadb(slabinfos, "data_20160610_0220_20160610_1000")
    # extract_frames_ratio(slabinfos)
    aoi_steep(slabinfos)


if __name__ == '__main__':
    main()
