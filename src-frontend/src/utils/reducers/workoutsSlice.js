import {createApi} from '@reduxjs/toolkit/query/react';
import {baseQueryWithReauth} from './baseQueryWithReauth';


/**
 * Converts a date string with timezone to local timezone
 * @param {string} dateString - Date string in format '2025-06-28T18:04:59+01:00'
 * @returns {string} Date string in local timezone without timezone info
 */
export const convertToLocalTimezone = (dateString) => {
    if (!dateString) return dateString;
    const date = new Date(dateString);
    return date.toISOString().split('.')[0];
};

/**
 * Adds local timezone offset to a date string that doesn't have timezone info
 * @param {string} dateString - Date string in format '2025-06-28T18:04:59'
 * @returns {string} Date string with local timezone offset
 */
export const addLocalTimezone = (dateString) => {
    if (!dateString) return dateString;
    const date = new Date(dateString);
    const offset = -date.getTimezoneOffset();
    const offsetHours = Math.floor(Math.abs(offset) / 60);
    const offsetMinutes = Math.abs(offset) % 60;
    const offsetSign = offset >= 0 ? '+' : '-';
    const offsetString = `${offsetSign}${String(offsetHours).padStart(2, '0')}:${String(offsetMinutes).padStart(2, '0')}`;
    return `${dateString}${offsetString}`;
};


export const workoutsApi = createApi({
    reducerPath: 'workoutsApi',
    baseQuery: baseQueryWithReauth,
    tagTypes: ['Workout'],
    keepUnusedDataFor: 60 * 60 * 3, // 3 hours (default is 60)
    endpoints: (builder) => ({
        getWorkouts: builder.query({
            query: (params = {}) => ({
                url: `workout/`, //?${new URLSearchParams(params).toString()}
                method: 'GET',
                params: params,
            }),
            transformResponse: (response) => {
                const today = new Date();
                const currentDay = today.getDay(); // 0 (Sun) - 6 (Sat)

                // This week's Monday
                const thisMonday = new Date(today);
                const diffToMonday = (currentDay === 0 ? -6 : 1) - currentDay;
                thisMonday.setDate(today.getDate() + diffToMonday);

                return response.map(workout => {
                    const date = new Date(workout.start_datetime);
                    // Reset hours to midnight for both dates to count whole days
                    const activityDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
                    const todayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
                    // Calculate difference in days
                    const daysAgo = Math.floor((todayDate - activityDate) / (1000 * 60 * 60 * 24));
                    return {
                        ...workout,
                        start_datetime_fmt: {
                            epoch: Math.floor(date.getTime() / 1000), // Unix epoch in seconds
                            date_iso: date.toLocaleDateString('en-CA'), // Canadian locale uses YYYY-MM-DD format by default
                            date_readable: date.toLocaleDateString('en-US', {
                                weekday: 'short',
                                month: 'short',
                                day: 'numeric'
                            }), // Mon, Jan 5
                            time_24h: date.toLocaleTimeString('en-US', {
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: false
                            }), // HH:MM
                            weeksAgo: Math.floor((thisMonday - date) / (7 * 24 * 60 * 60 * 1000)) + 1,
                            days_ago: daysAgo, // Number of whole days ago
                        },
                        start_datetime: convertToLocalTimezone(workout.start_datetime), // convert to local timezone
                    };
                });
            },
            // providesTags: (result = []) => result.map(({id}) => ({type: 'Workout', id})),
            providesTags: (result = []) => result.length ? [...result.map(({id}) => ({ type: 'Workout', id })), { type: 'Workout' }] : [{ type: 'Workout' }],
        }),
        getWorkoutById: builder.query({
            query: (id) => ({
                url: `workout/${id}/`,
                method: 'GET',
            }),
            transformResponse: (response) => {
                const date = new Date(response.start_datetime);
                return {
                    ...response,
                    start_datetime_obj: {
                        epoch: Math.floor(date.getTime() / 1000), // Unix epoch in seconds
                        date_iso: date.toLocaleDateString('en-CA'), // Canadian locale uses YYYY-MM-DD format by default
                        date_readable: date.toLocaleDateString('en-US', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric'
                        }), // Mon, Jan 5
                        time_24h: date.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit', hour12: false}) // HH:MM
                    },
                    start_datetime: convertToLocalTimezone(response.start_datetime),
                };
            },
            providesTags: (result, error, id) => [{type: 'Workout', id}],
        }),
        addWorkout: builder.mutation({
            query: (newWorkout) => ({
                url: 'workout/',
                method: 'POST',
                body: {
                    ...newWorkout,
                    start_datetime: addLocalTimezone(newWorkout.start_datetime), // add timezone
                },
            }),
            invalidatesTags: ['Workout'],
        }),
        updateWorkout: builder.mutation({
            query: ({id, ...patch}) => ({
                url: `workout/${id}/`,
                method: 'PATCH',
                body: {
                    ...patch,
                    // Only modify start_datetime if it exists in the patch
                    ...(patch.start_datetime && {
                        start_datetime: addLocalTimezone(patch.start_datetime) // add timezone
                    }),
                },
            }),
            invalidatesTags: (result, error, {id}) => [{type: 'Workout', id}],
        }),
        deleteWorkout: builder.mutation({
            query: (id) => ({
                url: `workout/${id}/`,
                method: 'DELETE',
            }),
            invalidatesTags: (result, error, id) => [{type: 'Workout', id}],
        }),
    }),
});

export const {
    useGetWorkoutsQuery,
    useGetWorkoutByIdQuery,
    useAddWorkoutMutation,
    useUpdateWorkoutMutation,
    useDeleteWorkoutMutation,
} = workoutsApi;