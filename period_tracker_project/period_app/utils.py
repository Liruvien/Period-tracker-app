from datetime import timedelta

def calculate_cycle_phases(menstruation_phase_start, menstruation_phase_end, cycle_length, months_to_predict=12):
    menstruation_duration = (menstruation_phase_end - menstruation_phase_start).days + 1
    phases = []

    for month in range(months_to_predict):
        cycle_start = menstruation_phase_start + timedelta(days=cycle_length * month)
        menstruation_start = cycle_start
        menstruation_end = menstruation_start + timedelta(days=menstruation_duration - 1)

        follicular_start = menstruation_end + timedelta(days=1)
        follicular_end = follicular_start + timedelta(days=(cycle_length - menstruation_duration - 14))

        ovulation_start = follicular_end + timedelta(days=1)
        ovulation_end = ovulation_start

        luteal_start = ovulation_end + timedelta(days=1)
        luteal_end = menstruation_start + timedelta(days=cycle_length * (month + 1)) - timedelta(days=1)

        phases.append({
            'Menstruation': {
                'start': menstruation_start,
                'end': menstruation_end,
                'color': 'red'
            },
            'Follicular': {
                'start': follicular_start,
                'end': follicular_end,
                'color': 'green'
            },
            'Ovulation': {
                'start': ovulation_start,
                'end': ovulation_end,
                'color': 'orange'
            },
            'Luteal': {
                'start': luteal_start,
                'end': luteal_end,
                'color': 'purple'
            }
        })
    return phases
