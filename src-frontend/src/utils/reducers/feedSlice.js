import {createApi} from '@reduxjs/toolkit/query/react';
import {baseQueryWithReauth} from './baseQueryWithReauth';
import {convertToLocalTimezone} from "./workoutsSlice";

export const feedApi = createApi({
    reducerPath: 'feedApi',
    baseQuery: baseQueryWithReauth,
    keepUnusedDataFor: 60 * 5, // 5 minutes (default is 60s)
    endpoints: (builder) => ({
        getFeedById: builder.query({
            query: (id) => ({
                url: `feed/${id}/`,
                method: 'GET',
            }),
            transformResponse: (response) => {
                // Convert timezone for all activites in the response
                return response.map(activity => {
                    const date = new Date(activity.workout__start_datetime);
                    const today = new Date();
                    // Reset hours to midnight for both dates to count whole days
                    const activityDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
                    const todayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
                    // Calculate difference in days
                    const daysAgo = Math.floor((todayDate - activityDate) / (1000 * 60 * 60 * 24));

                    return {
                        ...activity,
                        workout__start_datetime_fmt: {
                            epoch: Math.floor(date.getTime() / 1000), // Unix epoch in seconds
                            date_iso: date.toLocaleDateString('en-CA'), // Canadian locale uses YYYY-MM-DD format by default
                            date_readable: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }), // Mon, Jan 5
                            time_24h: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }), // HH:MM
                            days_ago: daysAgo, // Number of whole days ago
                        },
                        workout__start_datetime: convertToLocalTimezone(activity.workout__start_datetime), // convert to local timezone
                    };
                });
            },
            providesTags: (result, error, id) => [{type: 'Feed', id}],
        }),
    }),
});

export const {
    useGetFeedByIdQuery,
} = feedApi;