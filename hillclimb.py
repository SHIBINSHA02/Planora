import random


teachers = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
days = 5
periods_per_day = 6


def propose_random_timetable(teachers, days, periods):
    return [[random.choice(teachers) for _ in range(periods)] for _ in range(days)]


def evaluate_cost(timetable, teachers, days, periods):
    cost = 0
    teacher_load = {t: 0 for t in teachers}

    for day in range(days):
        teachers_in_day = set()
        for period in range(periods):
            teacher = timetable[day][period]
            teacher_load[teacher] += 1

            if teacher in teachers_in_day:
                cost += 1000 
            else:
                teachers_in_day.add(teacher)

            if period == periods - 1:
                cost += 10  

    expected_load = (days * periods) // len(teachers)
    for t in teachers:
        if teacher_load[t] > expected_load + 2 or teacher_load[t] < expected_load - 2:
            cost += 500 

    return cost


def mutate_timetable(timetable, teachers):
    new_timetable = [day[:] for day in timetable]
    day = random.randint(0, len(timetable) - 1)
    period = random.randint(0, len(timetable[0]) - 1)
    new_timetable[day][period] = random.choice(teachers)  
    return new_timetable


def hill_climb_timetable(teachers, days, periods, max_iterations=1000):
    current_timetable = propose_random_timetable(teachers, days, periods)
    current_cost = evaluate_cost(current_timetable, teachers, days, periods)

    for i in range(max_iterations):
        new_timetable = mutate_timetable(current_timetable, teachers)
        new_cost = evaluate_cost(new_timetable, teachers, days, periods)

        if new_cost < current_cost:
            current_timetable = new_timetable
            current_cost = new_cost
            print(f"Iteration {i+1}: Improved Cost = {current_cost}")

        if current_cost == 0:
            print("Optimal timetable found!")
            break

    return current_timetable, current_cost

best_timetable, best_cost = hill_climb_timetable(teachers, days, periods_per_day, max_iterations=10000)

print("\nBest Timetable Found:")
for day_index, day in enumerate(best_timetable):
    print(f"Day {day_index + 1}: {day}")
print("Best Cost:", best_cost)