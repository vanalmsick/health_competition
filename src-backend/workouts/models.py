import time
from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from custom_user.models import CustomUser
from competition.scorer import trigger_workout_change, trigger_workout_delete

# Create your models here.

SPORT_TYPE_GROUPS = [
    ('GROUP_ANY', 'Group: All Sports'),
    ('GROUP_RUNNING', 'Group: Running (Run / Trail / Treadmill)'),
    ('GROUP_BIKING', 'Group: Biking/Cycling (Except E-Bike)'),
    ('GROUP_WALKING', 'Group: Walking (Walk / Wheelchair / Elliptical / Stepper)'),
    ('GROUP_RACKET', 'Group: Racket Sports (Tennis / Squash / Badminton / Pickleball / Racquetball / Table Tennis)'),
    ('GROUP_SOCIAL', 'Group: Social Sports (Soccer / Golf)'),
    ('GROUP_CLASSES_CARDIO', 'Group: Cardio Gym Classes (Crossfit / HIIT)'),
    ('GROUP_CLASSES_MINDFUL', 'Group: Mindfulness Classes (Yoga / Pilates)'),
    ('GROUP_WATER_ACTIVE', 'Group: Active Water Sports (Swim / Canoe / Kayak / Kitesurf / Rowing / Surfing / Windsurf)'),
]

SPORT_TYPES = [
    ('Badminton', 'Badminton'),
    ('Ride', 'Biking/Cycling'),
    ('EBikeRide', 'Biking/Cycling (E-Bike)'),
    ('GravelRide', 'Biking/Cycling (Gravel)'),
    ('Handcycle', 'Biking/Cycling (Handcycle)'),
    ('Velomobile', 'Biking/Cycling (Velomobile)'),
    ('VirtualRide', 'Biking/Cycling (Virtual)'),
    ('Canoeing', 'Canoe'),
    ('Crossfit', 'Crossfit'),
    ('Elliptical', 'Elliptical'),
    ('Golf', 'Golf'),
    ('HighIntensityIntervalTraining', 'High Intensity Interval Training (HIIT)'),
    ('Hike', 'Hike'),
    ('IceSkate', 'Ice Skate'),
    ('InlineSkate', 'Inline Skate'),
    ('Kayaking', 'Kayak'),
    ('Kitesurf', 'Kitesurf'),
    ('MountainBikeRide', 'Mountain-Biking/Cycling'),
    ('EMountainBikeRide', 'Mountain-Biking/Cycling (E-Bike)'),
    ('Pickleball', 'Pickleball'),
    ('Pilates', 'Pilates'),
    ('Racquetball', 'Racquetball'),
    ('RockClimbing', 'Rock Climbing'),
    ('Rowing', 'Rowing (Outdoor)'),
    ('VirtualRow', 'Rowing (Virtual)'),
    ('Run', 'Run'),
    ('TrailRun', 'Run (Trail)'),
    ('VirtualRun', 'Run (Treadmill / Vitual)'),
    ('Sail', 'Sail'),
    ('Skateboard', 'Skateboard'),
    ('AlpineSki', 'Ski (Alpine)'),
    ('BackcountrySki', 'Ski (Backcountry)'),
    ('NordicSki', 'Ski (Nordic)'),
    ('RollerSki', 'Ski (Roller/Inliner)'),
    ('Snowboard', 'Snowboard'),
    ('Soccer', 'Soccer / Football'),
    ('Squash', 'Squash'),
    ('StairStepper', 'Stair Stepper'),
    ('StandUpPaddling', 'Stand-up Paddling'),
    ('Surfing', 'Surf'),
    ('Swim', 'Swim'),
    ('TableTennis', 'Table Tennis'),
    ('Tennis', 'Tennis'),
    ('Walk', 'Walk'),
    ('Snowshoe', 'Walk (Snowshoe)'),
    ('WeightTraining', 'Weight Training'),
    ('Wheelchair', 'Wheelchair'),
    ('Windsurf', 'Windsurf'),
    ('Workout', 'Workout / Other'),
    ('Yoga', 'Yoga'),
]

# MET (Metabolic Equivalent) Source https://pacompendium.com/adult-compendium/
SPORT_MET = {
    'Badminton': {1: 5.0, 2: 5.5, 3: 7.0, 4: 9.0},
    'Ride': {1: 4.3, 2: 7.0, 3: 9.0, 4: 12.0},
    'EBikeRide': {1: 4.0, 2: 6.0, 3: 6.8, 4: 7.0},
    'GravelRide': {1: 4.3, 2: 7.0, 3: 9.0, 4: 12.0},
    'Handcycle': {1: 4.3, 2: 7.0, 3: 9.0, 4: 12.0},
    'Velomobile': {1: 4.3, 2: 7.0, 3: 9.0, 4: 12.0},
    'VirtualRide': {1: 4.3, 2: 7.0, 3: 9.0, 4: 12.0},
    'Canoeing': {1: 2.8, 2: 3.5, 3: 5.8, 4: 12.0},
    'Crossfit': {1: 3.5, 2: 5.0, 3: 6.0, 4: 7.5},
    'Elliptical': {1: 3.0, 2: 5.0, 3: 7.0, 4: 9.0},
    'Golf': {1: 3.5, 2: 4.3, 3: 4.5, 4: 4.8},
    'HighIntensityIntervalTraining': {1: 5.0, 2: 7.0, 3: 9.0, 4: 11.0},
    'Hike': {1: 3.8, 2: 5.3, 3: 6.0, 4: 6.5},
    'IceSkate': {1: 7.5, 2: 9.8, 3: 12.3, 4: 15.5},
    'InlineSkate': {1: 7.5, 2: 9.8, 3: 12.3, 4: 15.5},
    'Kayaking': {1: 5.0, 2: 7.0, 3: 9.0, 4: 13.5},
    'Kitesurf': {1: 8.0, 2: 9.5, 3: 11.0, 4: 12.5},
    'MountainBikeRide': {1: 7.0, 2: 9.0, 3: 11.0, 4: 14.0},
    'EMountainBikeRide': {1: 6.0, 2: 8.0, 3: 8.8, 4: 9.0},
    'Pickleball': {1: 5.0, 2: 5.5, 3: 7.0, 4: 9.0},
    'Pilates': {1: 1.8, 2: 2.8, 3: 4.0, 4: 5.5},
    'Racquetball': {1: 5.5, 2: 7.0, 3: 8.5, 4: 10.0},
    'RockClimbing': {1: 5.8, 2: 7.3, 3: 8.8, 4: 10.5},
    'Rowing': {1: 5.0, 2: 7.5, 3: 11.0, 4: 14.0},
    'VirtualRow': {1: 5.0, 2: 7.5, 3: 11.0, 4: 14.0},
    'Run': {1: 7.8, 2: 10.5, 3: 11.8, 4: 13.0},
    'TrailRun': {1: 7.8, 2: 10.5, 3: 11.8, 4: 13.0},
    'VirtualRun': {1: 7.8, 2: 10.5, 3: 11.8, 4: 13.0},
    'Sail': {1: 3.0, 2: 3.3, 3: 4.5, 4: 9.3},
    'Skateboard': {1: 5.0, 2: 6.0, 3: 6.8, 4: 8.5},
    'AlpineSki': {1: 4.3, 2: 6.3, 3: 7.3, 4: 8.0},
    'BackcountrySki': {1: 6.8, 2: 8.5, 3: 9.5, 4: 11.3},
    'NordicSki': {1: 8.5, 2: 11.3, 3: 13.5, 4: 14.0},
    'RollerSki': {1: 6.8, 2: 8.5, 3: 9.5, 4: 11.3},
    'Snowboard': {1: 4.3, 2: 6.3, 3: 7.5, 4: 8.0},
    'Soccer': {1: 3.5, 2: 5.5, 3: 7.0, 4: 9.5},
    'Squash': {1: 5.0, 2: 7.3, 3: 9.0, 4: 12.0},
    'StairStepper': {1: 5.5, 2: 6.0, 3: 8.0, 4: 11.0},
    'StandUpPaddling': {1: 2.8, 2: 3.8, 3: 5.0, 4: 9.8},
    'Surfing': {1: 3.0, 2: 5.0, 3: 7.0, 4: 9.0},
    'Swim': {1: 5.8, 2: 8.0, 3: 9.8, 4: 10.5},
    'TableTennis': {1: 3.5, 2: 4.0, 3: 5.5, 4: 7.0},
    'Tennis': {1: 5.0, 2: 6.0, 3: 6.8, 4: 8.0},
    'Walk': {1: 3.0, 2: 3.8, 3: 4.8, 4: 5.5},
    'Snowshoe': {1: 5.0, 2: 5.8, 3: 6.8, 4: 7.5},
    'WeightTraining': {1: 3.0, 2: 3.5, 3: 5.0, 4: 6.0},
    'Wheelchair': {1: 3.3, 2: 3.8, 3: 5.3, 4: 6.3},
    'Windsurf': {1: 5.0, 2: 7.0, 3: 11.0, 4: 14.0},
    'Workout': {1: 2.5, 2: 4.0, 3: 6.0, 4: 8.0},
    'Yoga': {1: 2.0, 2: 3.0, 3: 4.0, 4: 6.0},
}

INTENSITY_CATEGORIES = [
    (1, 'Easy (Could do another one later today)'),
    (2, 'Moderate (Done for today but tomorrow is a new day)'),
    (3, 'Hard (Will definitely feel this workout tomorrow)'),
    (4, "All Out (Can't do another one tomorrow)")
]


class Workout(models.Model):
    """Workout - user logged workout"""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, blank=False, primary_key=False)

    sport_type = models.CharField(null=False, max_length=40, choices=SPORT_TYPES)
    start_datetime = models.DateTimeField(null=False)
    duration = models.DurationField(null=False)
    intensity_category = models.IntegerField(null=True, choices=INTENSITY_CATEGORIES)
    kcal = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    distance = models.DecimalField(null=True, max_digits=7, decimal_places=2)

    strava_id = models.BigIntegerField(unique=True, null=True)
    strava_intensity_avg_watts = models.DecimalField(null=True, max_digits=7, decimal_places=2)

    @property
    def duration_seconds(self):
        return self.duration.seconds

    def __str__(self):
        """str print-out of model entry"""
        return f"{self.start_datetime} - {self.sport_type} ({self.duration / (1_000 * 60)} min / {self.kcal} kcal)"

    def __init__(self, *args, **kwargs):
        """ save initial field values to be able to detect changes """
        super().__init__(*args, **kwargs)
        self._original = self._dict

    @property
    def _dict(self):
        """ dict of current fields and values - to detect changes """
        return {f.name: (round(float(getattr(self, f.name)), 2) if isinstance(getattr(self, f.name), Decimal) or isinstance(getattr(self, f.name), float) else getattr(self, f.name)) for f in self._meta.fields}

    def get_changed_fields(self):
        """ check which fields have changed """
        current = self._dict
        return {
            k: (v, current.get(k))
            for k, v in self._original.items()
            if v != current.get(k)
        }

    def save(self, *args, **kwargs):
        """ trigger recalculation of points_capped if workout changes """
        is_create = self.pk is None
        if self.intensity_category is None or self.intensity_category == "":
            self.intensity_category = 2
        scaling_kcal = float((1 if kwargs.get('user', None) is None else kwargs.get('user').scaling_kcal) if self.user is None else self.user.scaling_kcal)
        if self.kcal is None or self.kcal == "":
            self.kcal = SPORT_MET.get(self.sport_type, SPORT_MET['Workout'])[self.intensity_category] * 75 * (self.duration.seconds / (60 * 60)) * scaling_kcal # default human 75kg scaled up/down by scaler
        super().save(*args, **kwargs)
        changed = self.get_changed_fields()
        trigger_workout_change(
            instance=self,
            new=is_create,
            changes=changed
        )
        self._original = self._dict  # reset

    def delete(self, *args, **kwargs):
        """ trigger recalculation of points_capped if workout deleted """
        trigger_workout_delete(
            instance=self
        )
        super().delete(*args, **kwargs)