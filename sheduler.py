import random
import numpy as np
from collections import defaultdict

class MultiClassTimetableScheduler:
    def __init__(self):
        self.teachers = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
        self.subjects = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
        self.classrooms = ['Class_A', 'Class_B', 'Class_C']
        self.days = 5
        self.periods_per_day = 6
        
        # Subject requirements per week per classroom
        self.subject_periods = {
            'S1': 5,
            'S2': 4,
            'S3': 7,
            'S4': 6,
            'S5': 4,
            'S6': 4
        }
        
        # Teacher workload tracking: [teacher][day] = number of classes
        self.teacher_daily_load = {}
        for teacher in self.teachers:
            self.teacher_daily_load[teacher] = [0] * self.days
        
        # Cost matrix for adjacency: [teacher][day][period]
        self.teacher_costs = {}
        for teacher in self.teachers:
            self.teacher_costs[teacher] = [[0 for _ in range(self.periods_per_day)] 
                                         for _ in range(self.days)]
        
        # Timetable: [classroom][day][period] = (teacher, subject)
        self.timetables = {}
        for classroom in self.classrooms:
            self.timetables[classroom] = [[None for _ in range(self.periods_per_day)] 
                                        for _ in range(self.days)]
        
        # Track subject assignments per classroom
        self.subject_counts = {}
        for classroom in self.classrooms:
            self.subject_counts[classroom] = {subject: 0 for subject in self.subjects}
    
    def get_available_teachers(self, day, period):
        """Get teachers who can take a class (not exceeding 3 per day, minimum cost)"""
        available = []
        
        for teacher in self.teachers:
            # Check if teacher hasn't exceeded daily limit
            if self.teacher_daily_load[teacher][day] < 3:
                available.append(teacher)
        
        if not available:
            return []
        
        # Among available teachers, find those with minimum cost
        min_cost = float('inf')
        min_cost_teachers = []
        
        for teacher in available:
            cost = self.teacher_costs[teacher][day][period]
            if cost < min_cost:
                min_cost = cost
                min_cost_teachers = [teacher]
            elif cost == min_cost:
                min_cost_teachers.append(teacher)
        
        return min_cost_teachers
    
    def get_needed_subjects(self, classroom):
        """Get subjects that still need periods for a specific classroom"""
        needed = []
        for subject, required in self.subject_periods.items():
            if self.subject_counts[classroom][subject] < required:
                needed.append(subject)
        return needed
    
    def increment_adjacent_costs(self, teacher, day, period):
        """Increment cost for adjacent periods of the assigned teacher"""
        # Previous period
        if period > 0:
            self.teacher_costs[teacher][day][period - 1] += 1
        
        # Next period
        if period < self.periods_per_day - 1:
            self.teacher_costs[teacher][day][period + 1] += 1
    
    def is_teacher_adjacent(self, teacher, day, period):
        """Check if teacher has adjacent classes in any classroom"""
        # Check previous period
        if period > 0:
            for classroom in self.classrooms:
                prev_assignment = self.timetables[classroom][day][period - 1]
                if prev_assignment and prev_assignment[0] == teacher:
                    return True
        
        # Check next period
        if period < self.periods_per_day - 1:
            for classroom in self.classrooms:
                next_assignment = self.timetables[classroom][day][period + 1]
                if next_assignment and next_assignment[0] == teacher:
                    return True
        
        return False
    
    def assign_period(self, classroom, day, period):
        """Assign a teacher and subject to a specific period in a classroom"""
        # Get available teachers
        available_teachers = self.get_available_teachers(day, period)
        
        if not available_teachers:
            print(f"⚠️  No available teachers for {classroom} Day {day+1} Period {period+1}")
            return False
        
        # Get subjects that still need periods for this classroom
        needed_subjects = self.get_needed_subjects(classroom)
        
        if not needed_subjects:
            return False  # All subjects completed for this classroom
        
        # Try to find a valid assignment
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            # Randomly select from available teachers
            teacher = random.choice(available_teachers)
            
            # Check if teacher would have adjacent classes
            if self.is_teacher_adjacent(teacher, day, period):
                attempts += 1
                continue
            
            # Randomly select from needed subjects
            subject = random.choice(needed_subjects)
            
            # Make the assignment
            self.timetables[classroom][day][period] = (teacher, subject)
            self.subject_counts[classroom][subject] += 1
            self.teacher_daily_load[teacher][day] += 1
            
            # Increment adjacent costs for this teacher
            self.increment_adjacent_costs(teacher, day, period)
            
            return True
        
        # If we can't find a valid assignment, try to force assign
        for teacher in available_teachers:
            if not self.is_teacher_adjacent(teacher, day, period):
                subject = needed_subjects[0]
                self.timetables[classroom][day][period] = (teacher, subject)
                self.subject_counts[classroom][subject] += 1
                self.teacher_daily_load[teacher][day] += 1
                self.increment_adjacent_costs(teacher, day, period)
                return True
        
        print(f"⚠️  Could not assign {classroom} Day {day+1} Period {period+1}")
        return False
    
    def generate_timetable(self):
        """Generate timetables for all classrooms"""
        print("Generating timetables for all classrooms...")
        
        # Reset everything
        self.__init__()
        
        # Assign periods for each classroom
        for day in range(self.days):
            for period in range(self.periods_per_day):
                for classroom in self.classrooms:
                    self.assign_period(classroom, day, period)
        
        return self.validate_timetables()
    
    def validate_timetables(self):
        """Validate if timetables meet all constraints"""
        print("\nValidating timetables...")
        
        valid = True
        
        # Check subject period requirements for each classroom
        for classroom in self.classrooms:
            print(f"\n{classroom}:")
            for subject, required in self.subject_periods.items():
                actual = self.subject_counts[classroom][subject]
                status = "✅" if actual == required else "❌"
                print(f"  {subject}: {actual}/{required} {status}")
                if actual != required:
                    valid = False
        
        # Check teacher daily load
        print("\nTeacher Daily Loads:")
        for teacher in self.teachers:
            loads = self.teacher_daily_load[teacher]
            max_load = max(loads)
            status = "✅" if max_load <= 3 else "❌"
            print(f"  {teacher}: {loads} (max: {max_load}) {status}")
            if max_load > 3:
                valid = False
        
        # Check for adjacent teacher assignments
        print("\nChecking teacher adjacency...")
        adjacent_violations = 0
        for day in range(self.days):
            for period in range(self.periods_per_day - 1):
                teachers_current = set()
                teachers_next = set()
                
                for classroom in self.classrooms:
                    if self.timetables[classroom][day][period]:
                        teachers_current.add(self.timetables[classroom][day][period][0])
                    if self.timetables[classroom][day][period + 1]:
                        teachers_next.add(self.timetables[classroom][day][period + 1][0])
                
                # Check for common teachers
                common_teachers = teachers_current.intersection(teachers_next)
                if common_teachers:
                    adjacent_violations += len(common_teachers)
        
        if adjacent_violations > 0:
            print(f"⚠️  Adjacent teacher violations: {adjacent_violations}")
            valid = False
        else:
            print("✅ No adjacent teacher violations")
        
        print(f"\n{'✅ All validations passed!' if valid else '❌ Validation failed!'}")
        return valid
    
    def print_timetables(self):
        """Print timetables for all classrooms"""
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for classroom in self.classrooms:
            print(f"\n{'='*70}")
            print(f"TIMETABLE FOR {classroom}")
            print('='*70)
            
            # Header
            print(f"{'Day':<12}", end="")
            for period in range(1, self.periods_per_day + 1):
                print(f"Period {period:<10}", end="")
            print()
            print("-" * 70)
            
            # Days
            for day in range(self.days):
                print(f"{days_names[day]:<12}", end="")
                for period in range(self.periods_per_day):
                    if self.timetables[classroom][day][period]:
                        teacher, subject = self.timetables[classroom][day][period]
                        print(f"{teacher}-{subject:<10}", end="")
                    else:
                        print(f"{'FREE':<14}", end="")
                print()
    
    def print_teacher_summary(self):
        """Print teacher workload summary"""
        print(f"\n{'='*50}")
        print("TEACHER WORKLOAD SUMMARY")
        print('='*50)
        
        days_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        
        for teacher in self.teachers:
            print(f"\n{teacher}:")
            print(f"  Daily loads: {dict(zip(days_names, self.teacher_daily_load[teacher]))}")
            print(f"  Total classes: {sum(self.teacher_daily_load[teacher])}")
            
            # Show which classes this teacher teaches
            teacher_schedule = []
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    for classroom in self.classrooms:
                        assignment = self.timetables[classroom][day][period]
                        if assignment and assignment[0] == teacher:
                            teacher_schedule.append(f"{days_names[day]}-P{period+1}({classroom})")
            
            if teacher_schedule:
                print(f"  Schedule: {', '.join(teacher_schedule)}")

# Example usage
def main():
    scheduler = MultiClassTimetableScheduler()
    
    print("Subject Requirements:")
    for subject, periods in scheduler.subject_periods.items():
        print(f"  {subject}: {periods} periods/week")
    
    print(f"\nTotal periods per classroom: {sum(scheduler.subject_periods.values())}")
    print(f"Available slots per classroom: {scheduler.days * scheduler.periods_per_day}")
    
    # Generate timetable
    success = scheduler.generate_timetable()
    
    if success:
        scheduler.print_timetables()
        scheduler.print_teacher_summary()
    else:
        print("Failed to generate completely valid timetable")
        scheduler.print_timetables()
        scheduler.print_teacher_summary()

if __name__ == "__main__":
    main()