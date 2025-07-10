import random
import copy
from collections import defaultdict

class ImprovedTimetableScheduler:
    def __init__(self):
        self.teachers = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
        self.subjects = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
        self.classrooms = ['Class_A', 'Class_B', 'Class_C']
        self.days = 5
        self.periods_per_day = 6
        
        # Subject requirements per week per classroom
        self.subject_periods = {
            'S1': 5, 'S2': 4, 'S3': 7, 'S4': 6, 'S5': 4, 'S6': 4
        }
        
        # Configuration parameters
        self.max_daily_load = 4  # Increased from 3 to 4
        self.allow_adjacent = True  # Allow adjacent periods for same teacher
        self.max_consecutive = 2  # Maximum consecutive periods for same teacher
        
        self.reset_data_structures()
    
    def reset_data_structures(self):
        """Reset all data structures"""
        # Global teacher schedule: [teacher][day][period] = classroom (or None)
        self.teacher_schedule = {}
        for teacher in self.teachers:
            self.teacher_schedule[teacher] = [[None for _ in range(self.periods_per_day)]
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
        
        # Track teacher daily loads
        self.teacher_daily_load = {}
        for teacher in self.teachers:
            self.teacher_daily_load[teacher] = [0] * self.days

    def count_consecutive_periods(self, teacher, day, period):
        """Count consecutive periods for a teacher on a specific day around a period"""
        consecutive = 1  # Current period
        
        # Count backwards
        p = period - 1
        while p >= 0 and self.teacher_schedule[teacher][day][p] is not None:
            consecutive += 1
            p -= 1
        
        # Count forwards
        p = period + 1
        while p < self.periods_per_day and self.teacher_schedule[teacher][day][p] is not None:
            consecutive += 1
            p += 1
        
        return consecutive

    def is_teacher_available(self, teacher, day, period):
        """Check if teacher is available at specific time with improved constraints"""
        # Check if teacher is already assigned to another classroom
        if self.teacher_schedule[teacher][day][period] is not None:
            return False
        
        # Check daily load limit
        if self.teacher_daily_load[teacher][day] >= self.max_daily_load:
            return False
        
        # Check consecutive periods constraint (if enabled)
        if not self.allow_adjacent:
            # Original strict adjacency check
            if period > 0 and self.teacher_schedule[teacher][day][period - 1] is not None:
                return False
            if period < self.periods_per_day - 1 and self.teacher_schedule[teacher][day][period + 1] is not None:
                return False
        else:
            # Allow adjacent but limit consecutive periods
            if self.count_consecutive_periods(teacher, day, period) > self.max_consecutive:
                return False
        
        return True

    def get_teacher_preference_score(self, teacher, day, period):
        """Calculate preference score for teacher assignment (higher is better)"""
        score = 0
        
        # Prefer balanced daily loads
        current_load = self.teacher_daily_load[teacher][day]
        avg_load = sum(self.teacher_daily_load[teacher]) / self.days
        if current_load < avg_load:
            score += 10
        
        # Prefer middle periods over first/last
        if 1 <= period <= 4:
            score += 5
        
        # Slight preference for not having isolated periods
        has_adjacent = False
        if period > 0 and self.teacher_schedule[teacher][day][period - 1] is not None:
            has_adjacent = True
        if period < self.periods_per_day - 1 and self.teacher_schedule[teacher][day][period + 1] is not None:
            has_adjacent = True
        
        if has_adjacent and self.allow_adjacent:
            score += 2
        
        return score

    def get_available_teachers_ranked(self, day, period):
        """Get available teachers ranked by preference score"""
        available = []
        for teacher in self.teachers:
            if self.is_teacher_available(teacher, day, period):
                score = self.get_teacher_preference_score(teacher, day, period)
                available.append((teacher, score))
        
        # Sort by score (descending) and add some randomness
        available.sort(key=lambda x: x[1] + random.random() * 2, reverse=True)
        return [teacher for teacher, _ in available]

    def get_subject_priority_score(self, classroom, subject):
        """Calculate priority score for subject assignment (higher is more urgent)"""
        required = self.subject_periods[subject]
        assigned = self.subject_counts[classroom][subject]
        remaining = required - assigned
        
        if remaining <= 0:
            return -1  # Already complete
        
        # Base score is the deficit
        score = remaining * 10
        
        # Add urgency based on percentage completion
        completion_rate = assigned / required
        if completion_rate < 0.5:  # Less than 50% complete
            score += 20
        elif completion_rate < 0.8:  # Less than 80% complete
            score += 10
        
        # Add weight based on total periods required
        score += required
        
        return score

    def get_priority_subjects_ranked(self, classroom):
        """Get subjects ordered by priority score"""
        subjects_with_scores = []
        for subject in self.subjects:
            score = self.get_subject_priority_score(classroom, subject)
            if score > 0:  # Only include subjects that need more periods
                subjects_with_scores.append((subject, score))
        
        # Sort by score (descending) with some randomness
        subjects_with_scores.sort(key=lambda x: x[1] + random.random(), reverse=True)
        return [subject for subject, _ in subjects_with_scores]

    def assign_teacher_to_slot(self, teacher, classroom, day, period, subject):
        """Assign teacher to a specific time slot"""
        self.teacher_schedule[teacher][day][period] = classroom
        self.timetables[classroom][day][period] = (teacher, subject)
        self.subject_counts[classroom][subject] += 1
        self.teacher_daily_load[teacher][day] += 1

    def remove_teacher_from_slot(self, teacher, classroom, day, period, subject):
        """Remove teacher from a specific time slot"""
        self.teacher_schedule[teacher][day][period] = None
        self.timetables[classroom][day][period] = None
        self.subject_counts[classroom][subject] -= 1
        self.teacher_daily_load[teacher][day] -= 1

    def can_swap_assignments(self, slot1, slot2):
        """Check if two assignments can be swapped"""
        (classroom1, day1, period1) = slot1
        (classroom2, day2, period2) = slot2
        
        if self.timetables[classroom1][day1][period1] is None or self.timetables[classroom2][day2][period2] is None:
            return False
        
        teacher1, subject1 = self.timetables[classroom1][day1][period1]
        teacher2, subject2 = self.timetables[classroom2][day2][period2]
        
        # Temporarily remove both assignments
        self.remove_teacher_from_slot(teacher1, classroom1, day1, period1, subject1)
        self.remove_teacher_from_slot(teacher2, classroom2, day2, period2, subject2)
        
        # Check if swap is possible
        can_swap = (self.is_teacher_available(teacher1, day2, period2) and 
                   self.is_teacher_available(teacher2, day1, period1))
        
        # Restore original assignments
        self.assign_teacher_to_slot(teacher1, classroom1, day1, period1, subject1)
        self.assign_teacher_to_slot(teacher2, classroom2, day2, period2, subject2)
        
        return can_swap

    def generate_timetable_smart_greedy(self):
        """Generate timetable using improved greedy approach with local optimization"""
        print("Generating timetable using smart greedy approach...")
        
        self.reset_data_structures()
        
        # Phase 1: Initial assignment using improved greedy
        unassigned = []
        
        # Create all required assignments
        all_assignments = []
        for classroom in self.classrooms:
            for subject, required in self.subject_periods.items():
                for _ in range(required):
                    all_assignments.append((classroom, subject))
        
        # Sort assignments by priority
        all_assignments.sort(key=lambda x: self.subject_priority_score(x[0], x[1]), reverse=True)
        
        # Try to assign each requirement
        for classroom, subject in all_assignments:
            assigned = False
            
            # Get all possible time slots, ranked by preference
            time_slots = []
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    if self.timetables[classroom][day][period] is None:
                        # Calculate slot preference score
                        slot_score = self.calculate_slot_score(classroom, day, period)
                        time_slots.append((day, period, slot_score))
            
            # Sort by score with randomness
            time_slots.sort(key=lambda x: x[2] + random.random() * 5, reverse=True)
            
            # Try to assign to best available slot
            for day, period, _ in time_slots:
                available_teachers = self.get_available_teachers_ranked(day, period)
                
                if available_teachers:
                    teacher = available_teachers[0]  # Best ranked teacher
                    self.assign_teacher_to_slot(teacher, classroom, day, period, subject)
                    assigned = True
                    break
            
            if not assigned:
                unassigned.append((classroom, subject))
        
        # Phase 2: Try to resolve unassigned using swapping
        if unassigned:
            print(f"Attempting to resolve {len(unassigned)} unassigned periods using optimization...")
            self.resolve_unassigned_with_swapping(unassigned)
        
        return self.validate_timetables()

    def subject_priority_score(self, classroom, subject):
        """Calculate priority score for initial assignment"""
        required = self.subject_periods[subject]
        # Higher score for subjects with more periods
        return required * 10 + random.random() * 5

    def calculate_slot_score(self, classroom, day, period):
        """Calculate preference score for a time slot"""
        score = 0
        
        # Prefer middle periods
        if 1 <= period <= 4:
            score += 10
        
        # Prefer middle days
        if 1 <= day <= 3:
            score += 5
        
        # Check how many teachers are available (more options = better)
        available_count = len([t for t in self.teachers if self.is_teacher_available(t, day, period)])
        score += available_count * 2
        
        return score

    def resolve_unassigned_with_swapping(self, unassigned):
        """Try to resolve unassigned periods by swapping existing assignments"""
        max_swap_attempts = 100
        
        for classroom, subject in unassigned[:]:  # Copy list to avoid modification during iteration
            resolved = False
            
            for attempt in range(max_swap_attempts):
                # Find a random existing assignment that could potentially be swapped
                swap_candidates = []
                for c in self.classrooms:
                    for d in range(self.days):
                        for p in range(self.periods_per_day):
                            if self.timetables[c][d][p] is not None:
                                swap_candidates.append((c, d, p))
                
                if not swap_candidates:
                    break
                
                # Try random swaps
                random.shuffle(swap_candidates)
                
                for swap_classroom, swap_day, swap_period in swap_candidates[:20]:  # Limit attempts
                    # Try to move this assignment to make room
                    if self.try_relocate_assignment(swap_classroom, swap_day, swap_period, classroom, subject):
                        unassigned.remove((classroom, subject))
                        resolved = True
                        print(f"✅ Resolved {subject} for {classroom} through relocation")
                        break
                
                if resolved:
                    break
            
            if not resolved:
                print(f"⚠️  Could not resolve {subject} for {classroom}")

    def try_relocate_assignment(self, from_classroom, from_day, from_period, target_classroom, target_subject):
        """Try to relocate an assignment to make room for target assignment"""
        if self.timetables[from_classroom][from_day][from_period] is None:
            return False
        
        teacher, subject = self.timetables[from_classroom][from_day][from_period]
        
        # Temporarily remove the assignment
        self.remove_teacher_from_slot(teacher, from_classroom, from_day, from_period, subject)
        
        # Check if we can now assign the target
        available_teachers = self.get_available_teachers_ranked(from_day, from_period)
        can_assign_target = any(self.is_teacher_available(t, from_day, from_period) for t in self.teachers)
        
        if can_assign_target and self.timetables[target_classroom][from_day][from_period] is None:
            # Try to find new slot for the displaced assignment
            new_slot_found = False
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    if (self.timetables[from_classroom][day][period] is None and 
                        self.is_teacher_available(teacher, day, period)):
                        # Move the displaced assignment
                        self.assign_teacher_to_slot(teacher, from_classroom, day, period, subject)
                        
                        # Assign target to the freed slot
                        target_teachers = self.get_available_teachers_ranked(from_day, from_period)
                        if target_teachers:
                            self.assign_teacher_to_slot(target_teachers[0], target_classroom, from_day, from_period, target_subject)
                            return True
                        else:
                            # Rollback
                            self.remove_teacher_from_slot(teacher, from_classroom, day, period, subject)
                            break
        
        # Restore original assignment if no solution found
        self.assign_teacher_to_slot(teacher, from_classroom, from_day, from_period, subject)
        return False

    def validate_timetables(self):
        """Validate if timetables meet all constraints"""
        print("\nValidating timetables...")
        valid = True
        
        # Check subject period requirements
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
            status = "✅" if max_load <= self.max_daily_load else "❌"
            print(f"  {teacher}: {loads} (max: {max_load}) {status}")
            if max_load > self.max_daily_load:
                valid = False
        
        # Check for teacher conflicts
        print("\nChecking teacher conflicts...")
        conflicts = 0
        for day in range(self.days):
            for period in range(self.periods_per_day):
                teachers_in_period = []
                for classroom in self.classrooms:
                    if self.timetables[classroom][day][period]:
                        teacher = self.timetables[classroom][day][period][0]
                        teachers_in_period.append(teacher)
                
                if len(teachers_in_period) != len(set(teachers_in_period)):
                    conflicts += 1
                    print(f"  ⚠️  Conflict on Day {day+1} Period {period+1}: {teachers_in_period}")
        
        if conflicts == 0:
            print("✅ No teacher conflicts")
        else:
            print(f"❌ {conflicts} teacher conflicts found")
            valid = False
        
        # Check consecutive periods constraint
        if self.allow_adjacent:
            print("\nChecking consecutive periods constraint...")
            violations = 0
            for teacher in self.teachers:
                for day in range(self.days):
                    consecutive = 0
                    max_consecutive = 0
                    for period in range(self.periods_per_day):
                        if self.teacher_schedule[teacher][day][period] is not None:
                            consecutive += 1
                            max_consecutive = max(max_consecutive, consecutive)
                        else:
                            consecutive = 0
                    
                    if max_consecutive > self.max_consecutive:
                        violations += 1
                        print(f"  ⚠️  {teacher} has {max_consecutive} consecutive periods on day {day+1}")
            
            if violations == 0:
                print("✅ No consecutive period violations")
            else:
                print(f"❌ {violations} consecutive period violations")
                valid = False
        
        print(f"\n{'✅ All validations passed!' if valid else '❌ Validation failed!'}")
        return valid

    def solve_with_backtracking(self):
        """Solve using backtracking as fallback"""
        slots = []
        for day in range(self.days):
            for period in range(self.periods_per_day):
                for classroom in self.classrooms:
                    slots.append((classroom, day, period))
        
        random.shuffle(slots)
        return self.backtrack_solve(slots, 0)

    def backtrack_solve(self, slots, slot_index):
        """Recursive backtracking function"""
        if slot_index >= len(slots):
            return True
        
        classroom, day, period = slots[slot_index]
        needed_subjects = self.get_priority_subjects_ranked(classroom)
        
        if not needed_subjects:
            return self.backtrack_solve(slots, slot_index + 1)
        
        available_teachers = self.get_available_teachers_ranked(day, period)
        
        if not available_teachers:
            return self.backtrack_solve(slots, slot_index + 1)
        
        for teacher in available_teachers:
            for subject in needed_subjects:
                self.assign_teacher_to_slot(teacher, classroom, day, period, subject)
                
                if self.backtrack_solve(slots, slot_index + 1):
                    return True
                
                self.remove_teacher_from_slot(teacher, classroom, day, period, subject)
        
        return False

    def generate_timetable_iterative(self):
        """Generate timetable with multiple strategies"""
        max_attempts = 5
        
        for attempt in range(max_attempts):
            print(f"Attempt {attempt + 1}...")
            
            if self.generate_timetable_smart_greedy():
                print("✅ Successfully generated timetable with smart greedy!")
                return True
            
            print(f"❌ Smart greedy attempt {attempt + 1} failed")
        
        # Fallback to backtracking
        print("Trying backtracking approach...")
        self.reset_data_structures()
        
        if self.solve_with_backtracking():
            print("✅ Successfully generated timetable with backtracking!")
            return True
        
        print("❌ Failed to generate complete timetable")
        return False

    def print_timetables(self):
        """Print timetables for all classrooms"""
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for classroom in self.classrooms:
            print(f"\n{'='*70}")
            print(f"TIMETABLE FOR {classroom}")
            print('='*70)
            
            print(f"{'Day':<12}", end="")
            for period in range(1, self.periods_per_day + 1):
                print(f"Period {period:<10}", end="")
            print()
            print("-" * 70)
            
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
            
            schedule = []
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    classroom = self.teacher_schedule[teacher][day][period]
                    if classroom:
                        subject = self.timetables[classroom][day][period][1]
                        schedule.append(f"{days_names[day]}-P{period+1}({classroom}-{subject})")
            
            if schedule:
                print(f"  Schedule: {', '.join(schedule)}")

def main():
    scheduler = ImprovedTimetableScheduler()
    
    print("Subject Requirements:")
    for subject, periods in scheduler.subject_periods.items():
        print(f"  {subject}: {periods} periods/week")
    
    print(f"\nTotal periods per classroom: {sum(scheduler.subject_periods.values())}")
    print(f"Available slots per classroom: {scheduler.days * scheduler.periods_per_day}")
    print(f"Configuration: Max daily load = {scheduler.max_daily_load}, Allow adjacent = {scheduler.allow_adjacent}")
    
    success = scheduler.generate_timetable_iterative()
    
    if success:
        scheduler.print_timetables()
        scheduler.print_teacher_summary()
    else:
        print("Failed to generate a valid timetable. Try adjusting constraints.")

if __name__ == "__main__":
    main()
