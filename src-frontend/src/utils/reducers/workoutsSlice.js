import {createApi} from '@reduxjs/toolkit/query/react';
import {baseQueryWithReauth} from './baseQueryWithReauth';


/**
 * Converts a date string with timezone to local timezone
 * @param {string} dateString - Date string in format '2025-06-28T18:04:59+01:00'
 * @returns {string} Date string in local timezone without timezone info
 */
export const convertToLocalTimezone = (dateString) => {
    if (!dateString) return dateString;
    const d = new Date(dateString);
    const pad = num => String(num).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T` +
           `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
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


export const dateFormatter = (dateString) => {
    const date = new Date(dateString);
    const dateDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    const today = new Date();
    const todayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const currentDay = today.getDay(); // 0 (Sun) - 6 (Sat)

    // prev week's Sunday
    const prevSunday = new Date(today);
    prevSunday.setDate(today.getDate() - ((currentDay !== 0) ? currentDay : 7)); // go back to Sunday
    const prevSundayDate = new Date(prevSunday.getFullYear(), prevSunday.getMonth(), prevSunday.getDate());

    // Calculate difference in days/weeks
    const daysAgo = Math.floor((todayDate - dateDate) / (24 * 60 * 60 * 1000));
    const weeksAgo = Math.floor((prevSundayDate - dateDate) / (7 * 24 * 60 * 60 * 1000)) + 1;

    return {
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
        weeksAgo: weeksAgo,
        days_ago: daysAgo,
    };
};


export const workoutsApi = createApi({
    reducerPath: 'workoutsApi',
    baseQuery: baseQueryWithReauth,
    tagTypes: ['Workout'],
    keepUnusedDataFor: 60 * 60 * 12, // 12 hours cache (default is 60)
    refetchOnMountOrArgChange: 60 * 60, // Refetch if older than 1 hour
    endpoints: (builder) => ({
        getWorkouts: builder.query({
            query: (params = {}) => ({
                url: `workout/`, //?${new URLSearchParams(params).toString()}
                method: 'GET',
                params: params,
            }),
            transformResponse: (response) => {
                return response.map(workout => {
                    return {
                        ...workout,
                        start_datetime_fmt: dateFormatter(workout.start_datetime), // format datetime
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
                return {
                    ...response,
                    start_datetime_fmt: dateFormatter(response.start_datetime),
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