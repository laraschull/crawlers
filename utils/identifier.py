def generate_inmate_id(name, dob=None):
    # need a way to generate an id for people without a dob
    if dob is None:  # method overloading, no dob means name is actually whole inmate
        inmate = name
        name = inmate.name
        dob = inmate.DOB

    first = name.first
    last = name.last
    try:
        yob = dob.year
    except(AttributeError):
        if dob is not None:
            yob = dob["year"]
        else:
            yob = dob
    yob = str(yob)
    return last + "_" + first + "_" + yob


def generate_record_id(state, inmate_num):
    state = state.upper()
    assert(len(state) == 2 or state == "FED")

    return state + "_" + inmate_num
