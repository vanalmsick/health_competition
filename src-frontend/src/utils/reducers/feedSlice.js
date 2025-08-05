import {createApi} from '@reduxjs/toolkit/query/react';
import {baseQueryWithReauth} from './baseQueryWithReauth';
import {convertToLocalTimezone, dateFormatter} from "./workoutsSlice";

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
                    return {
                        ...activity,
                        workout__start_datetime_fmt: dateFormatter(activity.workout__start_datetime), // format datetime
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