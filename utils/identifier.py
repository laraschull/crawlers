def generate_inmate_id(name, dob=None):
    if dob is None:  # method overloading, no dob means name is actually whole inmate
        inmate = name
        name = inmate.name
        dob = inmate.DOB

    first = name.first
    last = name.last
    try:
        yob = dob.year
    except AttributeError:
        yob = dob["year"]
    yob = str(yob)
    ret = last + "_" + first + "_" + yob

    return ret 


def generate_record_id(state, record_id_num):
    state = state.upper()
    assert(len(state) == 2 or state == "FED")

    ret = state + "_" + record_id_num

    return(ret)

