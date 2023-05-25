from cm_wizard.services.currency import format_price, try_parse_euro_cents


def test_parse_euro_cents():
    assert try_parse_euro_cents("1,23 €") == 123
    assert try_parse_euro_cents("1,23€") == 123
    assert try_parse_euro_cents("1,23") == 123
    assert try_parse_euro_cents("1.23 €") == 123
    assert try_parse_euro_cents("1.23€") == 123
    assert try_parse_euro_cents("1.23") == 123
    assert try_parse_euro_cents("1 €") is None
    assert try_parse_euro_cents("1€") is None
    assert try_parse_euro_cents("1") is None
    assert try_parse_euro_cents("a") is None


def test_format_price():
    assert format_price(0) == "0,00 €"
    assert format_price(1) == "0,01 €"
    assert format_price(10) == "0,10 €"
    assert format_price(100) == "1,00 €"
    assert format_price(99999) == "999,99 €"
