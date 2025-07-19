import {createApi} from '@reduxjs/toolkit/query/react';
import {baseQueryWithReauth} from './baseQueryWithReauth';

export const joinApi = createApi({
    reducerPath: 'joinApi',
    baseQuery: baseQueryWithReauth,
    endpoints: (builder) => ({
        joinCompetition: builder.mutation({
            query: (join_code) => ({
                url: `join/competition/${join_code}/`,
                method: 'POST',
            }),
        }),
        joinTeam: builder.mutation({
            query: (id) => ({
                url: `join/team/${id}/`,
                method: 'POST',
            }),
        }),
    }),
});

export const {
    useJoinCompetitionMutation,
    useJoinTeamMutation,
} = joinApi;