def default_currency(country):
    mapping={
        "Nigeria":"NGN",
        "Botswana":"BWP"
    }
    return mapping.get(country,"USD")
