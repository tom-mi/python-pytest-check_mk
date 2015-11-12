def assert_inventory_and_check_works_with_check_output(check, check_output):
    inventory = check.inventory(check_output)

    assert_well_formed_inventory(check, inventory)

    # run check for each item in inventory using default params
    for item, default_params in inventory:
        if default_params:
            params = getattr(check.check_file.module, default_params)
        else:
            params = None
        result = check.check(item, params, check_output)
        assert_well_formed_check_result(check, result)


def assert_well_formed_check_result(check, result):
    status = result[0]
    message = result[1]

    assert isinstance(status, int)
    assert 0 <= status <= 3

    assert isinstance(message, str)

    if check.has_perfdata:
        assert len(result) == 3
        perfdata = result[2]

        for entry in perfdata:
            assert_well_formed_perfdata_entry(entry)
    else:
        assert len(result) == 2


def assert_well_formed_inventory(check, inventory):
    can_have_multiple_items = '%s' in check.service_description

    if not can_have_multiple_items:
        assert len(inventory) <= 1

    for item, default_params in inventory:
        assert (item is None) != can_have_multiple_items
        if default_params is not None:
            assert hasattr(check.check_file.module, default_params)


def assert_well_formed_perfdata_entry(entry):
    assert 2 <= len(entry) <= 6

    assert isinstance(entry[0], str)
    assert type(entry[1]) in (int, float)
    for value in entry[2:]:
        assert (type(value) in (int, float)) or value == ''
