def json_merge_patch(target, patch):
    if isinstance(patch, dict):
        if not isinstance(target, dict):
            target = dict()

        for key, value in patch.items():
            if value is None:
                if key in target:
                    target.pop(key, None)
            else:
                target[key] = json_merge_patch(target.get(key), value)
        return target
    return patch
