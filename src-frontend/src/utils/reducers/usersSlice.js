import {createApi} from '@reduxjs/toolkit/query/react';
import {baseQueryWithReauth} from './baseQueryWithReauth';

export const usersApi = createApi({
    reducerPath: 'usersApi',
    baseQuery: baseQueryWithReauth,
    tagTypes: ['User'],
    keepUnusedDataFor: 60 * 60 * 3, // 3 hours (default is 60)
    endpoints: (builder) => ({
        getUsers: builder.query({
            query: (params = {}) => ({
                url: `user/`, //?${new URLSearchParams(params).toString()}
                method: 'GET',
                params: params,
            }),
            providesTags: (result = []) => {
                const tags = result.map(({ id }) => ({ type: 'User', id }));
                if (result.some(user => user.id === 'me')) {
                    tags.push({ type: 'User', id: 'me' });
                }
                tags.push({ type: 'User' });
                return tags;
            },
        }),
        getUserById: builder.query({
            query: (id) => ({
                url: `user/${id}/`,
                method: 'GET',
            }),
            providesTags: (result, error, id) => {
                const tags = [{ type: 'User', id }];
                if (id === 'me') {
                    tags.push({ type: 'User', id: 'me' });
                }
                return tags;
            },
        }),
        addUser: builder.mutation({
            query: (newUser) => ({
                url: 'user/',
                method: 'POST',
                body: newUser,
            }),
            invalidatesTags: ['User'],
        }),
        updateUser: builder.mutation({
            query: ({id, ...patch}) => ({
                url: `user/${id}/`,
                method: 'PATCH',
                body: patch,
            }),
            invalidatesTags: (result, error, {id}) => {
                const tags = [{ type: 'User', id }];
                if (result?.my === true) {
                    tags.push({ type: 'User', id: 'me' });
                }
                return tags;
            },
        }),
        deleteUser: builder.mutation({
            query: (id) => ({
                url: `user/${id}/`,
                method: 'DELETE',
            }),
            invalidatesTags: (result, error, id) => {
                const tags = [{ type: 'User', id }];
                if (id === 'me') {
                    tags.push({ type: 'User', id: 'me' });
                }
                return tags;
            },
        }),
    }),
});

export const {
    useGetUsersQuery,
    useGetUserByIdQuery,
    useAddUserMutation,
    useUpdateUserMutation,
    useDeleteUserMutation,
} = usersApi;