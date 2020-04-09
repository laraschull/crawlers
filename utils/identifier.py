def generate_inmate_id(name, dob=None):
    # need a way to generate an id for people without a dob
    if dob is None:  # method overloading, no dob means name is actually whole inmate
        inmate = name
        name = inmate.name
        dob = inmate.DOB

    first = name.first
    last = name.last

    try:
        yob = str(dob.year)
    except(AttributeError):
        yob = str(dob)

    return last + "_" + first + "_" + yob


def generate_record_id(state, record_id_num):
    state = state.upper()
    assert(len(state) == 2 or state == "FED")

    return state + "_" + record_id_num
