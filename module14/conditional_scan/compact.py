"""Compact evidence view; detailed immutable dataset remains hash-addressed."""
import copy

from module14.scan import digest


def compact_remote(summary):
    result = copy.deepcopy(summary)
    shared = ('matching_card', 'reference_comparison', 'limitations', 'C1_scope', 'method_robustness_reason')
    first = next(iter(result['points'].values()))
    result['common_flavor_assumptions'] = {k: first['flavor'][k] for k in shared}
    for point in result['points'].values():
        for k in shared:
            if point['flavor'][k] != result['common_flavor_assumptions'][k]:
                raise ValueError('Different flavor assumptions across points')
            del point['flavor'][k]
        point['gates'] = {k: {'assessment': v['assessment'], 'details_sha256': digest(v),
                              **({'reason': v['reason']} if 'reason' in v else {})}
                          for k, v in point['gates'].items()}
    result['compact_view_note'] = 'Full gate/decay/family records remain in dataset_path with dataset_sha256. Gate detail hashes use module14.scan.digest canonical JSON. Complete scalar cards are retained here.'
    return result
