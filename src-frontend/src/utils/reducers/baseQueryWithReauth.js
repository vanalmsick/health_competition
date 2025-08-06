import {fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import * as Sentry from '@sentry/react';
import {throwErrorWithCode} from '../miscellaneous';

console.log('API URL:', process.env.REACT_APP_BACKEND_URL);

const baseQuery = fetchBaseQuery({
    baseUrl: (process.env.REACT_APP_BACKEND_URL || '') + '/api/',
    prepareHeaders: (headers) => {
        const token = localStorage.getItem('access_token');
        headers.set('Content-Type', 'application/json');
        if (token) {
            headers.set('Authorization', `Bearer ${token}`);
        }
        return headers;
    },
});

export const baseQueryWithReauth = async (args, api, extraOptions) => {
    let result = await baseQuery(args, api, extraOptions);

    // report to Sentry if not 401 (login access token needs refreshing) and 429 (too many strava sync requests) and 404 (not found after entry deletion)
    if (result.error && result.error.status !== 401 && result.error.status !== 429 && result.error.status !== 404) {
        Sentry.withScope((scope) => {
            scope.setContext('RTK Query Request', {
                args,
                endpointName: api.endpoint, // might be undefined outside endpoint context
                extraOptions,
            });
            scope.setContext('RTK Query Error', {
                status: result.error.status,
                data: result.error.data,
                originalStatus: result.error.originalStatus,
            });
            scope.setTag('error.source', 'rtk-query');
            scope.setTag('error.type', 'network-or-server');
            Sentry.captureException(
                new Error(`RTK Query request failed: ${result.error.status}`)
            );
        });
    }

    // if 401 forbidden error refresh the access token
    if (result.error && result.error.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            const currentUrl = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = `/login?redirect=${currentUrl}`; // force redirect
            throw throwErrorWithCode('(Error 401) The user is not authenticated (no refresh token). Please re-login.', 401);
        }

        // Try to refresh the token
        const refreshResult = await baseQuery(
            {
                url: '/token/refresh/',
                method: 'POST',
                body: {refresh: refreshToken},
            },
            api,
            extraOptions
        );

        if (refreshResult.data.access) {
            // Save new tokens
            localStorage.setItem('access_token', refreshResult.data.access);
            if (refreshResult.data.refresh) {
                localStorage.setItem('refresh_token', refreshResult.data.refresh);
            }

            // Retry original request
            result = await baseQuery(args, api, extraOptions);
        } else {
            const currentUrl = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = `/login?redirect=${currentUrl}`; // force redirect
            throw throwErrorWithCode('(Error 401) The user is not authenticated (refresh token expired). Please re-login.', 401);
        }
    }

    return result;
};