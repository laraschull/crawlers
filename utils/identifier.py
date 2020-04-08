def generate_inmate_id(name, dob=None):
    if dob is None:  # method overloading, no dob means name is actually whole inmate
        inmate = name
        name = inmate.name
        dob = inmate.DOB

    first = name.first
    last = name.last
    try:
        year = dob.year
    except(AttributeError):
        year = dob["year"]
    year = str(year)

    try:
        month = dob.month
    except(AttributeError):
        month = dob["month"]
    month = str(month)

    try:
        day = dob.day
    except(AttributeError):
        day = dob["day"]
    day = str(day)

    ret = last + "_" + first + "_" + year + "_" + "0" if len(month) == 1 else "" + month + "_" + "0" if len(day) == 1 else "" + day

    return(ret)


def generate_record_id(state, record_id_num):
    state = state.upper()
    assert(len(state) == 2 or state == "FED")

    ret = state + "_" + record_id_num

    return(ret)
