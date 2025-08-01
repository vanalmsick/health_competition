import {
    useAddWorkoutMutation,
    useDeleteWorkoutMutation, useGetWorkoutByIdQuery,
    useUpdateWorkoutMutation
} from "../utils/reducers/workoutsSlice";
import React, {useEffect, useState} from "react";
import {AddButton, DeleteButton, Modal, SaveButton, SingleForm} from "./basicComponents";

export const workoutTypes = {
    "Badminton": {"label": "Badminton", "label_short": "Badminton"},
    "Ride": {"label": "Biking/Cycling", "label_short": "Cycling"},
    "EBikeRide": {"label": "Biking/Cycling (E-Bike)", "label_short": "Cycling"},
    "GravelRide": {"label": "Biking/Cycling (Gravel)", "label_short": "Cycling"},
    "Handcycle": {"label": "Biking/Cycling (Handcycle)", "label_short": "Cycling"},
    "Velomobile": {"label": "Biking/Cycling (Velomobile)", "label_short": "Cycling"},
    "VirtualRide": {"label": "Biking/Cycling (Virtual)", "label_short": "Cycling"},
    "Canoeing": {"label": "Canoe", "label_short": "Canoe"},
    "Crossfit": {"label": "Crossfit", "label_short": "Crossfit"},
    "Elliptical": {"label": "Elliptical", "label_short": "Elliptical"},
    "Golf": {"label": "Golf", "label_short": "Golf"},
    "HighIntensityIntervalTraining": {"label": "High Intensity Interval Training (HIIT)", "label_short": "HIIT"},
    "Hike": {"label": "Hike", "label_short": "Hike"},
    "IceSkate": {"label": "Ice Skate", "label_short": "Ice Skate"},
    "InlineSkate": {"label": "Inline Skate", "label_short": "Inline Skate"},
    "Kayaking": {"label": "Kayak", "label_short": "Kayak"},
    "Kitesurf": {"label": "Kitesurf", "label_short": "Kitesurf"},
    "MountainBikeRide": {"label": "Mountain-Biking/Cycling", "label_short": "Mountain-Biking"},
    "EMountainBikeRide": {"label": "Mountain-Biking/Cycling (E-Bike)", "label_short": "Mountain-Biking"},
    "Pickleball": {"label": "Pickleball", "label_short": "Pickleball"},
    "Pilates": {"label": "Pilates", "label_short": "Pilates"},
    "Racquetball": {"label": "Racquetball", "label_short": "Racquetball"},
    "RockClimbing": {"label": "Rock Climbing", "label_short": "Climbing"},
    "Rowing": {"label": "Rowing (Outdoor)", "label_short": "Rowing"},
    "VirtualRow": {"label": "Rowing (Virtual)", "label_short": "Rowing"},
    "Run": {"label": "Run", "label_short": "Run"},
    "TrailRun": {"label": "Run (Trail)", "label_short": "Run"},
    "VirtualRun": {"label": "Run (Treadmill / Vitual)", "label_short": "Run"},
    "Sail": {"label": "Sail", "label_short": "Sail"},
    "Skateboard": {"label": "Skateboard", "label_short": "Skateboard"},
    "AlpineSki": {"label": "Ski (Alpine)", "label_short": "Ski"},
    "BackcountrySki": {"label": "Ski (Backcountry)", "label_short": "Ski"},
    "NordicSki": {"label": "Ski (Nordic)", "label_short": "Ski"},
    "RollerSki": {"label": "Ski (Roller/Inliner)", "label_short": "Ski"},
    "Snowboard": {"label": "Snowboard", "label_short": "Snowboard"},
    "Soccer": {"label": "Soccer / Football", "label_short": "Soccer"},
    "Squash": {"label": "Squash", "label_short": "Squash"},
    "StairStepper": {"label": "Stair Stepper", "label_short": "Stepper"},
    "StandUpPaddling": {"label": "Stand-up Paddling", "label_short": "SUP"},
    "Surfing": {"label": "Surf", "label_short": "Surf"},
    "Swim": {"label": "Swim", "label_short": "Swim"},
    "TableTennis": {"label": "Table Tennis", "label_short": "Table Tennis"},
    "Tennis": {"label": "Tennis", "label_short": "Tennis"},
    "Walk": {"label": "Walk", "label_short": "Walk"},
    "Snowshoe": {"label": "Walk (Snowshoe)", "label_short": "Walk"},
    "WeightTraining": {"label": "Weight Training", "label_short": "Weights"},
    "Wheelchair": {"label": "Wheelchair", "label_short": "Wheelchair"},
    "Windsurf": {"label": "Windsurf", "label_short": "Windsurf"},
    "Workout": {"label": "Other Workout", "label_short": "Other"},
    "Yoga": {"label": "Yoga", "label_short": "Yoga"}
}


const fields = {

    "sport_type": {
        "type": "select",
        "required": true,
        "read_only": false,
        "label": "Sport type",
        "value": "Run",
        "width": "max-sm:w-full w-1/2",
        "autoFocus": true,
        "selectList": Object.entries(workoutTypes).map(([key, value]) => ({
          value: key,
          ...value
        }))
    },
    "start_datetime": {
        "type": "datetime-local",
        "required": true,
        "read_only": false,
        "label": "Start Date & Time",
        "width": "max-sm:w-full w-1/2",
    },
    "duration": {
        "type": "time",
        "required": true,
        "read_only": false,
        "label": "Duration (hh:mm:ss)",
        "width": "max-sm:w-full w-1/2",
    },
    "intensity_category": {
        "type": "select",
        "required": false,
        "read_only": false,
        "label": "Intensity",
        "value": 2,
        "width": "max-sm:w-full w-1/2",
        "selectList": [
            {
                "value": 1,
                "label": "Easy (Could do another one later today)"
            },
            {
                "value": 2,
                "label": "Moderate (Done for today but tomorrow is a new day)"
            },
            {
                "value": 3,
                "label": "Hard (Will definitely feel this workout tomorrow)"
            },
            {
                "value": 4,
                "label": "All Out (Can't do another one tomorrow)"
            }
        ]
    },
    "kcal": {
        "type": "decimal",
        "required": false,
        "read_only": false,
        "label": "Kcal",
        "max_digits": 7,
        "decimal_places": 2,
        "width": "max-sm:w-full w-1/2",
        "placeholder": "Estimated if left empty"
    },
    "distance": {
        "type": "decimal",
        "required": false,
        "read_only": false,
        "label": "Distance (km)",
        "max_digits": 7,
        "decimal_places": 2,
        "width": "max-sm:w-full w-1/2",
        "placeholder": "Only if applicable"
    }

}


export default function WorkoutForm({id, setModalState}) {

    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayString = yesterday.toISOString();
    const defaultValues = {
        "sport_type": "Run",
        "start_datetime": yesterdayString.substring(0, 10) + "T20:00",
        "duration": "00:30:10",
        "intensity_category": 1,
    };

    const [values, setValues] = useState({...defaultValues});
    const [fieldErrors, setFieldErrors] = useState({});
    const [formError, setFormError] = useState('');

    const {
        data: initWorkout,
        error: initError,
        isLoading: iniLoading
    } = useGetWorkoutByIdQuery(id, {skip: id === true});
    const [updateEntry, {
        data: updateData,
        error: updateError,
        isLoading: updateIsLoading,
        isSuccess: updateIsSuccess
    }] = useUpdateWorkoutMutation();
    const [createEntry, {
        data: createData,
        error: createError,
        isLoading: createIsLoading,
        isSuccess: createIsSuccess
    }] = useAddWorkoutMutation();
    const [deleteEntry, {
        error: deleteError,
        isLoading: deleteIsLoading,
        isSuccess: deleteIsSuccess
    }] = useDeleteWorkoutMutation();

    // Overall form error message
    useEffect(() => {
        if (initError !== undefined) {
            setFormError('Get Error (' + initError?.status?.toLocaleString() + ' ' + initError?.originalStatus?.toLocaleString() + '): ' + initError?.message);
        } else if (updateError !== undefined) {
            setFormError('Update Error (' + updateError?.status?.toLocaleString() + ' ' + updateError?.originalStatus?.toLocaleString() + '): ' + updateError?.message);
        } else if (createError !== undefined) {
            setFormError('Create Error (' + createError?.status?.toLocaleString() + ' ' + createError?.originalStatus?.toLocaleString() + '): ' + createError?.message);
        } else if (deleteError !== undefined) {
            setFormError('Delete Error (' + deleteError?.status?.toLocaleString() + ' ' + deleteError?.originalStatus?.toLocaleString() + '): ' + deleteError?.message);
        }
    }, [initError, updateError, createError, deleteError])

    // load current form values
    useEffect(() => {
        if (initWorkout !== undefined) {
            setValues({...initWorkout});
        }
    }, [initWorkout])

    // form action button left
    async function handleDiscard() {
        if (id !== true) {
            // delete workout
            try {
                const result = await deleteEntry(values.id).unwrap();
                console.log('Delete Workout success:', result);
                setModalState(false);
                document.body.classList.remove('body-no-scroll');
            } catch (err) {
                console.error('Delete Workout failed', err);
            }
        } else {
            // save and add another
            try {
                const result = await createEntry(values).unwrap();
                console.log('Create Workout success:', result);
                setValues({...defaultValues});
            } catch (err) {
                console.error('Create Workout failed', err);
                setFieldErrors(err.data);
            }
        }
    }

    // form action button right
    async function handleSubmit() {
        console.log('submit', id, values);
        if (id !== true) {
            // update workout
            try {
                const result = await updateEntry(values).unwrap();
                console.log('Update Workout success:', result);
                setModalState(false);
                document.body.classList.remove('body-no-scroll');
            } catch (err) {
                console.error('Update Workout failed', err);
                setFieldErrors(err.data);
            }
        } else {
            // create workout
            try {
                const result = await createEntry(values).unwrap();
                console.log('Create Workout success:', result);
                setModalState(false);
                document.body.classList.remove('body-no-scroll');
            } catch (err) {
                console.error('Create Workout failed', err);
                setFieldErrors(err.data);
            }
        }
    }

    return (
        <Modal title="Workout" landscape={true} setShowModal={setModalState}
               isLoading={iniLoading || updateIsLoading || createIsLoading || deleteIsLoading}>
            <SingleForm fields={fields} values={values} setValues={setValues} errors={fieldErrors}/>
            <div className="text-center text-red-500 text-xs italic">{formError}</div>
            <div className="relative flex justify-between items-center">
                {
                    (id !== true) ? (
                        <DeleteButton onClick={handleDiscard} label="Delete" highlighted={false} larger={true}/>
                    ) : (
                        <AddButton additionalClasses=" hover:text-green-800 " onClick={handleDiscard} label="Save and add another" highlighted={false}
                                   larger={true}/>
                    )
                }
                <SaveButton onClick={handleSubmit} label={(id !== true) ? "Update" : "Save"} highlighted={true}
                            larger={true}/>
            </div>
        </Modal>
    )
}