import {createApi} from '@reduxjs/toolkit/query/react';
import {baseQueryWithReauth} from './baseQueryWithReauth';

export const statsApi = createApi({
    reducerPath: 'statsApi',
    baseQuery: baseQueryWithReauth,
    keepUnusedDataFor: 60 * 5, // 5 minutes (default is 60s)
    endpoints: (builder) => ({
        getStatsById: builder.query({
            query: (id) => ({
                url: `stats/${id}/`,
                method: 'GET',
            }),
            providesTags: (result, error, id) => [{type: 'Stats', id}],
        }),
    }),
});

export const {
    useGetStatsByIdQuery,
} = statsApi;